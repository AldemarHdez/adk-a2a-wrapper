# translator_agent.py
import os
import logging
from adk_a2a_wrapper import CollaborativeAgent
from a2a.types import AgentSkill


class TranslatorAgent(CollaborativeAgent):
    async def process_response(self, response_text: str, context):
        """
        Process the translation response.
        In a real implementation, this would use the ADK agent's response.
        """
        # Extract target language from context if provided
        target_lang = "es"  # Default to Spanish
        if hasattr(context, 'context') and context.context:
            target_lang = context.context.get("target_language", "es")
        
        # The response_text already contains the translation from the LLM
        # Just format it nicely
        return f"[Translated to {target_lang}]: {response_text}"


def create_agent():
    skills = [
        AgentSkill(
            id="translate",
            name="Language Translation",
            description="Translates text between languages",
            tags=["translation", "language"],
            examples=[
                "Translate this to Spanish",
                "Convert this text to French",
                "Translate to Japanese"
            ],
            inputModes=["text/plain"],
            outputModes=["text/plain"]
        )
    ]
    
    agent = TranslatorAgent(
        name="translator_agent",
        model="gpt-4o-mini",
        description="Translation agent that converts text between languages",
        instruction="""You are a professional translator. When given text and a target language, 
        translate the text accurately while preserving the meaning and tone. 
        If no target language is specified, translate to Spanish.""",
        port=9001,
        api_key=os.getenv("OPENAI_API_KEY"),
        skills=skills,
        enable_streaming=False
    )
    agent.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_agent()
