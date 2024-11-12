import asyncio
import logging
from even_glasses.bluetooth_manager import GlassesManager
from even_glasses.commands import send_text
import redis.asyncio as aioredis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    manager = GlassesManager(left_address=None, right_address=None)
    connected = await manager.scan_and_connect()
    await send_text(manager=manager, text_message="Hello, I am connected.")

    if connected:
        # Initialize Redis client
        redis_client = aioredis.from_url("redis://localhost")

        async with redis_client.client() as conn:
            pubsub = conn.pubsub()
            await pubsub.subscribe("messages")

            try:
                while True:
                    message = await pubsub.get_message(ignore_subscribe_messages=True)
                    if message:
                        msg = message['data'].decode('utf-8')
                        await send_text(manager=manager, text_message=msg, duration=7)                    
                        await asyncio.sleep(0.01) 
            except KeyboardInterrupt:
                logger.info("Interrupted by user.")
            finally:
                await pubsub.unsubscribe("messages")
                await manager.disconnect_all()
    else:
        logger.error("Failed to connect to glasses.")

if __name__ == "__main__":
    asyncio.run(main())
