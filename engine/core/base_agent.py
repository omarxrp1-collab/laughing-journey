import asyncio

class BaseAgent:
    def __init__(self, name, bus, subscriptions=None):
        self.name = name
        self.bus = bus
        self.queue = asyncio.Queue()
        self.subscriptions = subscriptions or []
        bus.subscribe(self, self.subscriptions)

    async def publish(self, msg_type, payload, symbol=None, priority=5):
        await self.bus.publish(msg_type, payload, symbol=symbol, priority=priority)

    async def run(self):
        while True:
            msg = await self.queue.get()
            try:
                await self.handle(msg)
            except Exception as e:
                # يمكن لاحقاً إضافة LoggingAgent
                print(f"[{self.name}] Error: {e}")

    async def handle(self, msg):
        raise NotImplementedError