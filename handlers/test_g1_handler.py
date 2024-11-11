import asyncio
from g1_handler import G1Handler
handler = G1Handler()

async def main():
    await handler.connect()
    await handler.start_heartbeat()
    await handler.send_text_async("Hello World")
    
if __name__ == "__main__":
    asyncio.run(main())