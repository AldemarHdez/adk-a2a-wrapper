import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from adk_a2a_wrapper import create_a2a_agent
from dotenv import load_dotenv

load_dotenv()

# Create the reviewer agent
reviewer_agent = Agent(
    name="reviewer_agent",
    description="An agent that reviews and provides feedback on poems",
    instruction="You are a poetry critic. Review poems and provide constructive feedback. Be specific and helpful.",
    model=LiteLlm(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
)

# Create A2A server
server = create_a2a_agent(
    agent=reviewer_agent,
    port=8081,
    collaborators={
        "poet": "http://localhost:8080"
    }
)

if __name__ == "__main__":
    print("Starting Reviewer Agent on port 8081...")
    server.run()
