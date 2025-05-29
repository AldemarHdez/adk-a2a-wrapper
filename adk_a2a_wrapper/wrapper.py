import uuid
import logging
from typing import Dict, Any, Optional, List
import httpx
from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.apps.starlette_app import A2AStarletteApplication
from a2a.server.events.event_queue import EventQueue
from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
    Part,
    TextPart,
    DataPart,
    Message,
    MessageSendParams,
    SendMessageRequest,
    TaskState,
)
from google.genai import types
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from .models import AgentRequest, AgentResponse, SkillDefinition


class A2AAgentServer:
    """A2A server wrapper for ADK agents with skill support."""
    
    def __init__(
        self,
        agent: Agent,
        port: int,
        skills: Optional[List[SkillDefinition]] = None,
        collaborators: Optional[Dict[str, str]] = None,
        host: str = "0.0.0.0",
        enable_streaming: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        self.agent = agent
        self.port = port
        self.host = host
        self.skills = skills or []
        self.collaborators = collaborators or {}
        self.enable_streaming = enable_streaming
        self.logger = logger or logging.getLogger(agent.name)
        
        # Initialize A2A components
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name=agent.name,
            session_service=self.session_service,
        )
        self.task_store = InMemoryTaskStore()
        self.agent_card = self._create_agent_card()
        self.executor = self._create_executor()
    
    def add_skill(self, skill: SkillDefinition):
        """Add a skill definition to the agent."""
        self.skills.append(skill)
        # Update agent card with new skill
        self.agent_card = self._create_agent_card()
    
    def _create_agent_card(self) -> AgentCard:
        """Create A2A agent card with skills."""
        # Convert SkillDefinition to AgentSkill
        a2a_skills = []
        for skill in self.skills:
            a2a_skill = AgentSkill(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                tags=skill.tags,
                examples=skill.examples,
            )
            a2a_skills.append(a2a_skill)
        
        # Add default skill if no skills defined
        if not a2a_skills:
            a2a_skills.append(
                AgentSkill(
                    id="general",
                    name="General Processing",
                    description=f"{self.agent.name} general capabilities",
                    tags=["general"],
                )
            )
        
        return AgentCard(
            name=self.agent.name,
            description=self.agent.description or "ADK Agent",
            version="1.0",
            url=f"http://localhost:{self.port}/",
            capabilities=AgentCapabilities(
                streaming=self.enable_streaming,
                pushNotifications=False,
                stateTransitionHistory=True,
            ),
            defaultInputModes=["text/plain", "application/json"],
            defaultOutputModes=["text/plain", "application/json"],
            skills=a2a_skills,
        )
    
    def _get_skill_for_request(self, request: AgentRequest) -> Optional[SkillDefinition]:
        """Determine which skill to use for a request."""
        # If skill_id is specified, find it
        if request.skill_id:
            for skill in self.skills:
                if skill.id == request.skill_id:
                    return skill
        
        # Otherwise, use the first skill or None for general processing
        return self.skills[0] if self.skills else None
    
    def _create_executor(self) -> AgentExecutor:
        """Create the A2A executor."""
        parent = self
        
        class ADKExecutor(AgentExecutor):
            async def execute(self, context: RequestContext, event_queue: EventQueue):
                try:
                    # Extract input
                    user_input = context.get_user_input()
                    data = {}
                    skill_id = None
                    
                    if context.message and context.message.parts:
                        for part in context.message.parts:
                            if part.root.kind == "data":
                                data.update(part.root.data)
                                # Check for skill_id in data
                                skill_id = data.get("skill_id")
                    
                    # Create task updater
                    task_id = context.task_id or str(uuid.uuid4())
                    context_id = context.context_id or str(uuid.uuid4())
                    updater = TaskUpdater(event_queue, task_id, context_id)
                    
                    # Update task status
                    updater.submit()
                    updater.start_work()
                    
                    # Process with ADK
                    session_id = str(uuid.uuid4())
                    await parent.session_service.create_session(
                        app_name=parent.agent.name,
                        user_id="user1",
                        session_id=session_id
                    )
                    
                    # Create request object
                    request = AgentRequest(
                        message=user_input,
                        context=data,
                        session_id=session_id,
                        skill_id=skill_id
                    )
                    
                    # Process request
                    response = await parent.process_request(request, session_id)
                    
                    # Create response artifact
                    parts = [TextPart(text=response.message)]
                    if response.data:
                        parts.append(DataPart(data=response.data))
                    
                    updater.add_artifact(
                        parts=parts,
                        artifact_id="response",
                        name="response",
                    )
                    
                    updater.complete()
                    
                except Exception as e:
                    parent.logger.error(f"Error: {e}", exc_info=True)
                    if 'updater' in locals():
                        updater.failed(
                            updater.new_agent_message(
                                [TextPart(text=f"Error: {str(e)}")]
                            )
                        )
            
            async def cancel(self, context: RequestContext, event_queue: EventQueue):
                task_id = context.task_id
                if task_id:
                    updater = TaskUpdater(
                        event_queue, task_id, context.context_id or ""
                    )
                    updater.update_status(TaskState.canceled, final=True)
        
        return ADKExecutor()
    
    async def process_request(self, request: AgentRequest, session_id: str) -> AgentResponse:
        """Process request with ADK agent using appropriate skill."""
        try:
            # Get the skill for this request
            skill = self._get_skill_for_request(request)
            
            # Build prompt with skill context if available
            prompt = request.message
            if skill:
                prompt = f"[Using skill: {skill.name}] {request.message}"
            if request.context:
                prompt = f"{prompt}\n\nContext: {request.context}"
            
            # Run ADK agent
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
            
            return AgentResponse(
                message=response_text,
                status="success",
                session_id=session_id,
                skill_used=skill.id if skill else "general"
            )
            
        except Exception as e:
            self.logger.error(f"Error processing request: {e}")
            return AgentResponse(
                message=f"Error: {str(e)}",
                status="error",
                session_id=session_id
            )
    
    async def call_agent(self, agent_name: str, request: AgentRequest) -> AgentResponse:
        """Call another agent with skill support."""
        if agent_name not in self.collaborators:
            return AgentResponse(
                message=f"Agent {agent_name} not found",
                status="error"
            )
        
        try:
            from a2a.client.client import A2AClient
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                a2a_client = A2AClient(
                    httpx_client=client,
                    url=self.collaborators[agent_name]
                )
                
                # Prepare data with skill_id if specified
                data = request.context.copy() if request.context else {}
                if request.skill_id:
                    data["skill_id"] = request.skill_id
                
                parts = [Part(root=TextPart(text=request.message))]
                if data:
                    parts.append(Part(root=DataPart(data=data)))
                
                msg = Message(
                    messageId=str(uuid.uuid4()),
                    role="user",
                    parts=parts
                )
                
                req = SendMessageRequest(params=MessageSendParams(message=msg))
                resp = await a2a_client.send_message(req)
                
                # Extract response
                response_text = ""
                response_data = {}
                
                if resp and hasattr(resp, 'root') and hasattr(resp.root, 'result'):
                    result = resp.root.result
                    if hasattr(result, 'artifacts') and result.artifacts:
                        for artifact in result.artifacts:
                            for part in artifact.parts:
                                if part.root.kind == "text":
                                    response_text += part.root.text
                                elif part.root.kind == "data":
                                    response_data.update(part.root.data)
                
                return AgentResponse(
                    message=response_text,
                    status="success",
                    data=response_data
                )
                
        except Exception as e:
            self.logger.error(f"Error calling {agent_name}: {e}")
            return AgentResponse(
                message=f"Error calling {agent_name}: {str(e)}",
                status="error"
            )
    
    def build_app(self):
        """Build the Starlette application."""
        handler = DefaultRequestHandler(
            agent_executor=self.executor,
            task_store=self.task_store,
        )
        app = A2AStarletteApplication(self.agent_card, handler).build()
        return app
    
    def run(self):
        """Run the agent server."""
        import uvicorn
        uvicorn.run(self.build_app(), host=self.host, port=self.port)


def create_a2a_agent(
    agent: Agent,
    port: int,
    skills: Optional[List[SkillDefinition]] = None,
    collaborators: Optional[Dict[str, str]] = None,
    **kwargs
) -> A2AAgentServer:
    """Create an A2A server for an ADK agent with skill support.
    
    Args:
        agent: The ADK agent instance
        port: Port to run the server on
        skills: List of skill definitions for the agent
        collaborators: Dict mapping agent names to their URLs
        **kwargs: Additional arguments for A2AAgentServer
    
    Returns:
        A2AAgentServer instance
    """
    return A2AAgentServer(
        agent=agent,
        port=port,
        skills=skills,
        collaborators=collaborators,
        **kwargs
    )
