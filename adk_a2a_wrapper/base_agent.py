"""
Simplified base classes for creating A2A-enabled ADK agents.
"""
import uuid
import logging
from typing import Dict, Any, Optional, List
import httpx
from a2a.types import AgentSkill
from adk_a2a_wrapper import create_a2a_agent, SkillDefinition, AgentRequest, AgentResponse
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


class CollaborativeAgent:
    """Base class for collaborative ADK agents with A2A support."""
    
    def __init__(
        self,
        name: str,
        model: str,
        description: str,
        instruction: str,
        port: int,
        api_key: str,
        skills: Optional[List[AgentSkill]] = None,
        collaborators: Optional[Dict[str, str]] = None,
        tools: Optional[List] = None,
        enable_streaming: bool = False,
        host: str = "0.0.0.0",
        logger: Optional[logging.Logger] = None,
    ):
        self.name = name
        self.model = model
        self.description = description
        self.instruction = instruction
        self.port = port
        self.api_key = api_key
        self.skills = skills or []
        self.collaborators = collaborators or {}
        self.tools = tools or []
        self.enable_streaming = enable_streaming
        self.host = host
        self.logger = logger or logging.getLogger(name)
        
        # Create ADK agent
        self.adk_agent = Agent(
            name=name,
            description=description,
            instruction=instruction,
            model=LiteLlm(model=model, api_key=api_key),
            tools=tools,
        )
        
        # Convert AgentSkill to SkillDefinition
        skill_definitions = []
        for skill in self.skills:
            skill_def = SkillDefinition(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                tags=skill.tags or [],
                examples=skill.examples,
            )
            skill_definitions.append(skill_def)
        
        # Create A2A server with custom process_request
        self._server = None
        self._skill_definitions = skill_definitions
        self._setup_server()
    
    def _setup_server(self):
        """Set up the A2A server with custom processing."""
        parent = self
        
        # Create a custom A2A server class
        from adk_a2a_wrapper.wrapper import A2AAgentServer
        
        class CustomA2AServer(A2AAgentServer):
            async def process_request(self, request: AgentRequest, session_id: str) -> AgentResponse:
                """Override to use parent's process_response method."""
                try:
                    # First get the base ADK response
                    prompt = request.message
                    if request.context:
                        prompt = f"{request.message}\n\nContext: {request.context}"
                    
                    # Run ADK agent
                    from google.genai import types
                    content = types.Content(
                        role="user",
                        parts=[types.Part(text=prompt)]
                    )
                    
                    response_text = ""
                    async for event in self.runner.run_async(
                        user_id="user1",
                        session_id=session_id,
                        new_message=content
                    ):
                        if event.is_final_response() and event.content and event.content.parts:
                            response_text = event.content.parts[0].text
                            break
                    
                    # Now let the parent process the response
                    if hasattr(parent, 'process_response'):
                        response_text = await parent.process_response(response_text, request)
                    
                    return AgentResponse(
                        message=response_text,
                        status="success",
                        session_id=session_id,
                        skill_used=request.skill_id or "general"
                    )
                    
                except Exception as e:
                    parent.logger.error(f"Error processing request: {e}")
                    return AgentResponse(
                        message=f"Error: {str(e)}",
                        status="error",
                        session_id=session_id
                    )
        
        # Create the server instance
        self._server = CustomA2AServer(
            agent=self.adk_agent,
            port=self.port,
            skills=self._skill_definitions,
            collaborators=self.collaborators,
            host=self.host,
            enable_streaming=self.enable_streaming,
            logger=self.logger,
        )
    
    async def call_agent(
        self, 
        agent_name: str, 
        message: str, 
        data: Optional[Dict[str, Any]] = None,
        skill_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call another agent and get structured response."""
        request = AgentRequest(
            message=message,
            context=data or {},
            skill_id=skill_id
        )
        
        response = await self._server.call_agent(agent_name, request)
        
        return {
            "text": response.message,
            "status": response.status,
            "data": response.data,
            "skill_used": response.skill_used
        }
    
    async def process_response(self, response_text: str, context: AgentRequest) -> str:
        """
        Override this method to customize response processing.
        
        Args:
            response_text: The raw response from the ADK agent
            context: The original request context
            
        Returns:
            The processed response text
        """
        # Default implementation - just return the response
        return response_text
    
    def run(self):
        """Run the agent server."""
        if self._server:
            self.logger.info(f"Starting {self.name} on port {self.port}...")
            if self.skills:
                self.logger.info(f"Available skills: {[s.name for s in self.skills]}")
            if self.collaborators:
                self.logger.info(f"Collaborators: {list(self.collaborators.keys())}")
            self._server.run()
        else:
            self.logger.error("Server not initialized properly")
