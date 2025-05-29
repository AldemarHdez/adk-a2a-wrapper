# ADK-A2A Wrapper

A simple wrapper that enables Google ADK agents to communicate with each other using the A2A (Agent-to-Agent) protocol.

## Features

- Easy integration of A2A communication capabilities with ADK agents
- Support for agent-to-agent collaboration
- Skill-based agent capabilities
- Simple API for creating A2A-compliant ADK agents
- Built-in request/response models for standardized communication

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Agent
```python
from adk_a2a_wrapper import create_a2a_agent

# Create an A2A-enabled ADK agent
server = create_a2a_agent(
    agent=my_adk_agent,
    port=8080,
    collaborators={
        "other_agent": "http://localhost:8081"
    }
)

# Run the server
server.run()
```

### Agent with Skills
```python
from adk_a2a_wrapper import create_a2a_agent, SkillDefinition

# Define agent skills
skills = [
    SkillDefinition(
        id="analyze",
        name="Data Analyzer",
        description="Analyzes data and provides insights",
        tags=["analysis", "data"],
        examples=["Analyze this dataset", "What patterns do you see?"]
    ),
    SkillDefinition(
        id="summarize",
        name="Summarizer",
        description="Creates concise summaries",
        tags=["summary", "text"],
        examples=["Summarize this document", "Give me the key points"]
    )
]

# Create agent with skills
server = create_a2a_agent(
    agent=my_adk_agent,
    port=8080,
    skills=skills
)
```

## API Reference

### SkillDefinition
```python
class SkillDefinition:
    id: str                           # Unique skill identifier
    name: str                         # Human-readable name
    description: str                  # What the skill does
    tags: List[str]                  # Categorization tags
    examples: Optional[List[str]]     # Example prompts
    input_schema: Optional[Dict]      # Expected input format
    output_schema: Optional[Dict]     # Expected output format
```

### AgentRequest
```python
class AgentRequest:
    message: str                      # The message to process
    context: Dict[str, Any]          # Additional context
    session_id: Optional[str]        # Session identifier
    skill_id: Optional[str]          # Specific skill to use
```

### AgentResponse
```python
class AgentResponse:
    message: str                      # The response message
    status: str                      # Status (success/error)
    data: Dict[str, Any]            # Additional data
    session_id: Optional[str]        # Session identifier
    skill_used: Optional[str]        # Which skill was used
```

## Example

See the `example/` directory for a complete example with two collaborating agents:
- **Poem Agent**: Creates poems with different skills (haiku, sonnet, free verse)
- **Reviewer Agent**: Reviews and provides feedback on poems

```bash
# Run the poem agent
python example/poem_agent.py

# Run the reviewer agent
python example/reviewer_agent.py

# Test the collaboration
python example/test_collaboration.py
```

## Agent Communication

Agents can communicate with each other using the `call_agent` method:

```python
# Inside your agent's process_request method
response = await self.call_agent(
    "other_agent",
    AgentRequest(
        message="Help me with this task",
        context={"data": some_data},
        skill_id="specific_skill"  # Optional: request specific skill
    )
)
```
