# poem_agent_collab.py
import os
import logging
from adk_a2a_wrapper import CollaborativeAgent
from a2a.types import AgentSkill

# Simulated function from the original ADK poem agent
# In a real scenario, this would be imported from poem_agent.agent
def generate_poem(prompt: str) -> str:
    """
    Simulated poem generation function.
    In real use, this would be your original ADK agent logic.
    """
    # This is just a placeholder - in reality, you'd have your actual poem generation logic
    return f"A beautiful poem about: {prompt}\n\nRoses are red,\nViolets are blue,\n{prompt} is wonderful,\nAnd so are you!"


class PoemCollaborativeAgent(CollaborativeAgent):
    async def process_response(self, response_text: str, context):
        # Genera el poema usando la lógica original
        poem = generate_poem(response_text)
        
        # Ejemplo: Llama a otro agente colaborador (por ejemplo, un traductor)
        if "translator" in self.collaborators:
            translation = await self.call_agent(
                "translator",
                message=poem,
                data={"target_language": "es"}
            )
            translated_poem = translation.get("text", "")
            return f"Original Poem:\n{poem}\n\nTranslated Poem:\n{translated_poem}"
        else:
            return poem


def create_agent():
    skills = [
        AgentSkill(
            id="poem",
            name="Poem Generation",
            description="Generates poems on any topic",
            tags=["poem", "creative"],
            examples=["Write a poem about the sea", "Create a poem about love"],
            inputModes=["text/plain"],
            outputModes=["text/plain"]
        )
    ]
    
    agent = PoemCollaborativeAgent(
        name="poem_collab_agent",
        model="gpt-4o-mini",  # Using gpt-4o-mini for consistency
        description="Poem agent with collaboration abilities",
        instruction="Generate a poem and optionally collaborate with other agents.",
        port=9000,
        api_key=os.getenv("OPENAI_API_KEY"),
        skills=skills,
        collaborators={
            # Ejemplo: otro agente corriendo en localhost:9001
            "translator": "http://localhost:9001/"
        }
    )
    agent.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_agent()
