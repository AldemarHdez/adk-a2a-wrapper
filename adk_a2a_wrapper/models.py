from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class AgentRequest(BaseModel):
    """Standard A2A agent request format."""
    message: str = Field(..., description="The message to process")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the request")
    session_id: Optional[str] = Field(None, description="Session identifier for stateful interactions")


class AgentResponse(BaseModel):
    """Standard A2A agent response format."""
    message: str = Field(..., description="The response message")
    status: str = Field(default="success", description="Status of the response (success, error)")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional data returned by the agent")
    session_id: Optional[str] = Field(None, description="Session identifier for stateful interactions")
