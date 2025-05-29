# ADK-A2A Wrapper

A simple wrapper that enables Google ADK agents to communicate with each other using the A2A (Agent-to-Agent) protocol.

## Features

- Easy integration of A2A communication capabilities with ADK agents
- Support for agent-to-agent collaboration
- Simple API for creating A2A-compliant ADK agents
- Built-in request/response models for standardized communication

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from adk_a2a_wrapper import create_a2a_agent, AgentRequest

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

## Example

See the `example/` directory for a complete example with two collaborating agents.

```bash
# Run the poem agent
python example/poem_agent.py

# Run the reviewer agent
python example/reviewer_agent.py

# Test the collaboration
python example/test_collaboration.py
```
