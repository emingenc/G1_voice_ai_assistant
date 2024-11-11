import asyncio
import logging
from even_glasses.bluetooth_manager import GlassesManager
from even_glasses.commands import send_text

class G1Handler:
    def __init__(self):
        self.manager = GlassesManager(left_address=None, right_address=None)
        self.connected = False
        asyncio.create_task(self.manager.scan_and_connect())

    async def send_text_async(self, text: str):
        try:
            await send_text(self.manager, text)
        except Exception as e:
            logging.error(f"Error sending text to glasses: {e}")
            self.connected = False
