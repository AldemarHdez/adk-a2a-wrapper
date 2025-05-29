import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from adk_a2a_wrapper import create_a2a_agent
from dotenv import load_dotenv

load_dotenv()

# Create the poem agent
poem_agent = Agent(
    name="poem_agent",
    description="An agent that creates beautiful poems",
    instruction="You are a creative poet. Create poems based on user requests. Be creative and expressive.",
    model=LiteLlm(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
)

# Create A2A server with collaboration capability
server = create_a2a_agent(
    agent=poem_agent,
    port=8080,
    collaborators={
        "reviewer": "http://localhost:8081"
    }
)

if __name__ == "__main__":
    print("Starting Poem Agent on port 8080...")
    server.run()
