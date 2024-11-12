import logging
from typing import Optional, Callable
from langgraph_sdk import get_client
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import asyncio

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

    @classmethod
    async def create(cls, user_id: Optional[str] = None):
        """Async factory method to create and initialize LLMHandler"""
        instance = cls(user_id)
        await instance.initialize()
        return instance

    async def initialize(self):
        """Async initialization"""
        self.thread = await self.client.threads.create()
        self.logger.info(f"Thread created with ID: {self.thread['thread_id']}")
        return self

    async def generate_response(
        self, content: str, on_token: Callable[[str], None] = None
    ) -> str:
        """Generate a response from the LLM with token streaming."""
        if not self.thread:
            await self.initialize()
            
        self.logger.info(f"User input: {content}")
        result_chunks = []
        
        async for chunk in client.runs.stream(
                self.thread['thread_id'],  # Access id directly from thread object
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
                    if isinstance(content, list):
                        node = content[0].get("name", "")
                        if node == "upsert_memory":
                            self.logger.info(f"Memory upserted: {content}")
                            content = "Okay, I've noted that down."
                    if on_token and isinstance(content, str):
                        on_token(content)
                    result_chunks.append(content)
                    
        return result_chunks


