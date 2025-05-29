import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from adk_a2a_wrapper import create_a2a_agent, SkillDefinition
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

# Define skills for the poem agent
poem_skills = [
    SkillDefinition(
        id="haiku",
        name="Haiku Creator",
        description="Creates traditional Japanese haiku poems (5-7-5 syllable pattern)",
        tags=["poetry", "haiku", "japanese"],
        examples=[
            "Write a haiku about nature",
            "Create a haiku about the seasons",
            "Make a haiku about technology"
        ]
    ),
    SkillDefinition(
        id="sonnet",
        name="Sonnet Writer",
        description="Writes Shakespearean or Petrarchan sonnets",
        tags=["poetry", "sonnet", "classical"],
        examples=[
            "Write a sonnet about love",
            "Create a Shakespearean sonnet",
            "Compose a sonnet about time"
        ]
    ),
    SkillDefinition(
        id="free_verse",
        name="Free Verse Poet",
        description="Creates modern free verse poetry without strict structure",
        tags=["poetry", "modern", "free-form"],
        examples=[
            "Write a free verse poem about the city",
            "Create a modern poem about emotions",
            "Compose a free-form poem about dreams"
        ]
    )
]

# Create A2A server with skills and collaboration capability
server = create_a2a_agent(
    agent=poem_agent,
    port=8080,
    skills=poem_skills,
    collaborators={
        "reviewer": "http://localhost:8081"
    }
)

if __name__ == "__main__":
    print("Starting Poem Agent on port 8080...")
    print(f"Available skills: {[skill.name for skill in poem_skills]}")
    server.run()
