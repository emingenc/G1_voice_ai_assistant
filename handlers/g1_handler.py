import asyncio
import logging
from even_glasses.bluetooth_manager import GlassesManager
from even_glasses.commands import send_text

class G1Handler:
    def __init__(self):
        self.manager = GlassesManager()
        self.connected = False
        
    async def connect(self):
        """Initialize connection asynchronously"""
        try:
            await self.manager.scan_and_connect()
            await self.send_text_async("Connected to G1")
            await self.start_heartbeat()
            await self.send_text_async("Heartbeat started")
            self.connected = True
        except Exception as e:
            logging.error(f"Failed to connect to G1: {e}")
            self.connected = False

    async def start_heartbeat(self):
        """Continuous background updates for G1 glasses"""
        await self.manager.left_glass.start_heartbeat()  # Added parentheses
        await asyncio.sleep(0.2)  # Added await
        await self.manager.right_glass.start_heartbeat()  # Added parentheses
        await asyncio.sleep(0.2)  # Added await
        
    async def send_text_async(self, text: str):
        """Non-blocking text send"""
        if not self.connected:
            return
        try:
            await send_text(self.manager, text)
        except Exception as e:
            logging.error(f"Error sending text to G1: {e}")
