import asyncio
import logging
from even_glasses.bluetooth_manager import GlassesManager
from even_glasses.commands import send_text

class G1Handler:
    def __init__(self):
        self.manager = GlassesManager(left_address=None, right_address=None)
        self.connected = False
        self.text_buffer = ""

    # Add new method to initialize
    async def initialize(self):
        """Initialize the handler"""
        await self._init_async()

    async def _init_async(self):
        """Initialize connection asynchronously"""
        try:
            self.connected = await self._connect_async()
            if self.connected:
                logging.info("Successfully connected to G1 glasses")
                await self._send_text_async("G1 Glasses Connected...")
                asyncio.create_task(self.manager.left_glass.start_heartbeat())
                asyncio.create_task(self.manager.right_glass.start_heartbeat())
                
        except Exception as e:
            logging.error(f"Failed to connect to G1 glasses: {e}")
            self.connected = False

    async def _connect_async(self):
        try:
            connected = await self.manager.scan_and_connect()
            if not (self.manager.left_glass or self.manager.right_glass):
                logging.error("No glasses found during scan")
                return False
            return connected
        except Exception as e:
            logging.error(f"Connection error: {e}")
            return False

    def send_text(self, text: str):
        if not text.strip():
            return
            
        if self.connected:
            try:
                self.text_buffer += text
                if text.endswith(('.', '!', '?', '\n')) or len(self.text_buffer) > 50:
                    asyncio.create_task(self.send_text_async(self.text_buffer))
                    self.text_buffer = ""
            except Exception as e:
                logging.error(f"Failed to send text to glasses: {e}")
                self.connected = False
        else:
            logging.warning("G1 glasses not connected")

    async def send_text_async(self, text: str):
        try:
            await send_text(self.manager, text)
        except Exception as e:
            logging.error(f"Error sending text to glasses: {e}")
            self.connected = False

    async def cleanup(self):
        """Cleanup method to be called when shutting down"""
        if self.connected:
            try:
                await self.manager.disconnect_all()
                logging.info("G1 glasses disconnected")
            except Exception as e:
                logging.error(f"Error disconnecting G1 glasses: {e}")