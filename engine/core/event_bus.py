import asyncio
from collections import defaultdict

class EventBus:
    """
    حافلة أحداث بسيطة (In-Memory).
    كل وكيل يسجل أنواع الرسائل التي يهتم بها.
    """
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.lock = asyncio.Lock()

    def subscribe(self, agent, msg_types):
        for t in msg_types:
            self.subscribers[t].append(agent)

    async def publish(self, msg_type, payload, symbol=None, priority=5):
        # priority غير مستخدمة هنا (مكان لتطوير Queue متقدم)
        if msg_type not in self.subscribers:
            return
        for agent in list(self.subscribers[msg_type]):
            await agent.queue.put({
                "type": msg_type,
                "payload": payload,
                "symbol": symbol
            })