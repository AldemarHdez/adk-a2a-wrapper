from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class AgentRequest(BaseModel):
    """Standard A2A agent request format."""
    message: str = Field(..., description="The message to process")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the request")
    session_id: Optional[str] = Field(None, description="Session identifier for stateful interactions")
    skill_id: Optional[str] = Field(None, description="Specific skill to invoke")


class AgentResponse(BaseModel):
    """Standard A2A agent response format."""
    message: str = Field(..., description="The response message")
    status: str = Field(default="success", description="Status of the response (success, error)")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional data returned by the agent")
    session_id: Optional[str] = Field(None, description="Session identifier for stateful interactions")
    skill_used: Optional[str] = Field(None, description="The skill that was used to generate the response")


class SkillDefinition(BaseModel):
    """Definition of an agent skill."""
    id: str = Field(..., description="Unique identifier for the skill")
    name: str = Field(..., description="Human-readable name of the skill")
    description: str = Field(..., description="Detailed description of what the skill does")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the skill")
    examples: Optional[List[str]] = Field(None, description="Example prompts that trigger this skill")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Expected input format")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Expected output format")
