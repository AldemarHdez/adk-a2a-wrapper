# ADK-A2A Wrapper

A simple wrapper that enables Google ADK agents to communicate with each other using the A2A (Agent-to-Agent) protocol.

## Features

- Easy integration of A2A communication capabilities with ADK agents
- Support for agent-to-agent collaboration
- Skill-based agent capabilities
- Simple inheritance-based API with `CollaborativeAgent`
- Built-in request/response models for standardized communication

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Method 1: Using CollaborativeAgent (Recommended)

The easiest way is to inherit from `CollaborativeAgent` and override the `process_response` method:

```python
from adk_a2a_wrapper import CollaborativeAgent
from a2a.types import AgentSkill
# Import your original ADK agent logic
from my_agent.agent import my_processing_function

class MyCollaborativeAgent(CollaborativeAgent):
    async def process_response(self, response_text: str, context):
        # Use your original agent logic
        result = my_processing_function(response_text)
        
        # Optionally collaborate with other agents
        if "helper_agent" in self.collaborators:
            help_response = await self.call_agent(
                "helper_agent",
                message=result,
                data={"extra_info": "some_data"}
            )
            result = f"{result}\n\nHelper says: {help_response['text']}"
        
        return result

# Create and run the agent
agent = MyCollaborativeAgent(
    name="my_agent",
    model="gpt-4o-mini",
    description="My collaborative agent",
    instruction="Process requests and collaborate with other agents",
    port=8080,
    api_key=os.getenv("OPENAI_API_KEY"),
    skills=[AgentSkill(...)],
    collaborators={
        "helper_agent": "http://localhost:8081"
    }
)
agent.run()
```

### Method 2: Direct A2A Server Creation

For more control, you can create an A2A server directly:

```python
from adk_a2a_wrapper import create_a2a_agent, SkillDefinition

# Define skills
skills = [
    SkillDefinition(
        id="analyze",
        name="Data Analyzer",
        description="Analyzes data and provides insights",
        tags=["analysis", "data"]
    )
]

# Create A2A server
server = create_a2a_agent(
    agent=my_adk_agent,
    port=8080,
    skills=skills,
    collaborators={
        "other_agent": "http://localhost:8081"
    }
)
server.run()
```

## Complete Example: Poem Agent with Translation

### 1. Collaborative Poem Agent (port 9000)
```python
# poem_agent_collab.py
from adk_a2a_wrapper import CollaborativeAgent
from a2a.types import AgentSkill
from poem_agent.agent import generate_poem

class PoemCollaborativeAgent(CollaborativeAgent):
    async def process_response(self, response_text: str, context):
        # Generate poem using original logic
        poem = generate_poem(response_text)
        
        # Collaborate with translator
        if "translator" in self.collaborators:
            translation = await self.call_agent(
                "translator",
                message=poem,
                data={"target_language": "es"}
            )
            return f"Original:\n{poem}\n\nTranslated:\n{translation['text']}"
        return poem
```

### 2. Translator Agent (port 9001)
```python
# translator_agent.py
from adk_a2a_wrapper import CollaborativeAgent
from a2a.types import AgentSkill

class TranslatorAgent(CollaborativeAgent):
    async def process_response(self, response_text: str, context):
        target_lang = context.context.get("target_language", "es")
        return f"[{target_lang}]: {response_text}"
```

### 3. Test the Collaboration
```bash
# Terminal 1: Run translator
python translator_agent.py

# Terminal 2: Run poem agent
python poem_agent_collab.py

# Terminal 3: Test
curl -X POST http://localhost:9000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"text": "Write a poem about the ocean"}]
      }
    },
    "id": 1
  }'
```

## API Reference

### CollaborativeAgent

Base class for creating collaborative ADK agents:

```python
class CollaborativeAgent:
    def __init__(
        self,
        name: str,                    # Agent name
        model: str,                   # LLM model (e.g., "gpt-4o-mini")
        description: str,             # Agent description
        instruction: str,             # System instruction
        port: int,                    # Server port
        api_key: str,                 # API key for LLM
        skills: List[AgentSkill],     # Agent skills
        collaborators: Dict[str, str], # Other agents' URLs
        tools: List = None,           # ADK tools
        enable_streaming: bool = False,
        host: str = "0.0.0.0",
        logger: Logger = None
    )
    
    async def process_response(self, response_text: str, context) -> str:
        """Override this to customize response processing"""
        
    async def call_agent(self, agent_name: str, message: str, data: Dict = None) -> Dict:
        """Call another agent and get response"""
        
    def run(self):
        """Start the A2A server"""
```

## Examples

The `example/` directory contains:
- `poem_agent_collab.py` - Collaborative poem agent that uses translation
- `translator_agent.py` - Translation agent example
- `poem_agent.py` - Original skill-based poem agent
- `reviewer_agent.py` - Poem reviewer agent
- `test_collaboration.py` - Test script for agent communication

## Key Concepts

1. **Inherit from CollaborativeAgent**: Get A2A capabilities by inheritance
2. **Override process_response**: Customize how your agent processes responses
3. **Use original agent logic**: Import and use your existing ADK agent functions
4. **Collaborate easily**: Use `call_agent()` to communicate with other agents
5. **Define skills**: Use A2A AgentSkill to expose capabilities

## Repository Structure

```
adk-a2a-wrapper/
├── adk_a2a_wrapper/
│   ├── __init__.py
│   ├── base_agent.py      # CollaborativeAgent class
│   ├── models.py          # Request/Response models
│   └── wrapper.py         # Core A2A wrapper
├── example/
│   ├── poem_agent_collab.py  # Collaborative poem example
│   ├── translator_agent.py    # Translator example
│   └── ...
└── requirements.txt
```
