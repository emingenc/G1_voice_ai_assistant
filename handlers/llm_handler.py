import logging
from typing import Optional, Callable
from langgraph_sdk import get_client
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

URL = "http://localhost:8123"
client = get_client(url=URL)


load_dotenv()


class LLMHandler:
    def __init__(self, user_id: Optional[str] = None):
        self.graph_url = URL
        self.client = get_client(url=URL)
        self.user_id = user_id or "default_user"
        self.thread = None
        self.config = {
            "configurable": {},
            "user_id": self.user_id,
        }
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        
    async def generate_response(
        self, content: str, on_token: Callable[[str], None] = None
    ) -> str:
        """Generate a response from the LLM with token streaming.
        
        Args:
            content: The user input text
            on_token: Optional callback for streaming tokens
            
        Returns:
            The complete response text
        """
        self.logger.info(f"User input: {content}")
        self.thread = await client.threads.create()
        result_chunks = []
        # Stream
        async for chunk in client.runs.stream(
                self.thread['thread_id'],
                "agent",
                input={"messages": [HumanMessage(content=content)]},
                stream_mode="values",
            ):
            if chunk.data and chunk.event != "metadata":
                last_message = chunk.data['messages'][-1]
                msg_type = last_message['type']
                content = last_message['content']
                if msg_type == "ai":
                    self.logger.info(f"AI response: {content}")
                    if on_token:
                        on_token(content)
                    result_chunks.append(content)

                    
        return result_chunks


