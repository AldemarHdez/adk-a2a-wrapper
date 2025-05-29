import asyncio
import httpx
from a2a.client.client import A2AClient
from a2a.types import Message, Part, TextPart, MessageSendParams, SendMessageRequest
import uuid


async def test_agents():
    """Test the collaboration between poem and reviewer agents."""
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        # Connect to poem agent
        poem_client = A2AClient(httpx_client=client, url="http://localhost:8080/")
        
        # Request a poem
        print("\n=== Requesting a poem about nature ===")
        msg = Message(
            messageId=str(uuid.uuid4()),
            role="user",
            parts=[Part(root=TextPart(text="Write a short poem about a sunset over the ocean"))]
        )
        
        req = SendMessageRequest(params=MessageSendParams(message=msg))
        resp = await poem_client.send_message(req)
        
        # Extract poem
        poem_text = ""
        if resp and hasattr(resp, 'root') and hasattr(resp.root, 'result'):
            result = resp.root.result
            if hasattr(result, 'artifacts') and result.artifacts:
                for artifact in result.artifacts:
                    for part in artifact.parts:
                        if part.root.kind == "text":
                            poem_text = part.root.text
                            print(f"\nPoem:\n{poem_text}")
        
        # Now ask reviewer to review the poem
        print("\n=== Requesting review of the poem ===")
        reviewer_client = A2AClient(httpx_client=client, url="http://localhost:8081/")
        
        review_msg = Message(
            messageId=str(uuid.uuid4()),
            role="user",
            parts=[Part(root=TextPart(text=f"Please review this poem:\n\n{poem_text}"))]
        )
        
        review_req = SendMessageRequest(params=MessageSendParams(message=review_msg))
        review_resp = await reviewer_client.send_message(review_req)
        
        # Extract review
        if review_resp and hasattr(review_resp, 'root') and hasattr(review_resp.root, 'result'):
            result = review_resp.root.result
            if hasattr(result, 'artifacts') and result.artifacts:
                for artifact in result.artifacts:
                    for part in artifact.parts:
                        if part.root.kind == "text":
                            review_text = part.root.text
                            print(f"\nReview:\n{review_text}")


if __name__ == "__main__":
    print("Testing ADK agents with A2A communication...")
    print("Make sure both agents are running (poem_agent.py and reviewer_agent.py)")
    asyncio.run(test_agents())
