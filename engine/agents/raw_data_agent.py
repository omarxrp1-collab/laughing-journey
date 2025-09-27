import asyncio, time, random
from engine.core.base_agent import BaseAgent

class RawDataAgent(BaseAgent):
    def __init__(self, name, bus, symbols):
        super().__init__(name, bus, [])
        self.symbols = symbols
        self.buffers = {s: [] for s in symbols}

    async def run(self):
        while True:
            now = time.time()
            for sym in self.symbols:
                price = 50000 + random.uniform(-150,150) if sym=="BTCUSDT" else 3000 + random.uniform(-20,20)
                bar = {
                    "ts": now,
                    "open": price * 0.999,
                    "high": price * 1.001,
                    "low":  price * 0.998,
                    "close": price,
                    "volume": random.uniform(100,600)
                }
                buf = self.buffers[sym]
                buf.append(bar)
                if len(buf) > 500:
                    buf.pop(0)
                await self.publish("RAW_BAR", {"bar": bar}, symbol=sym, priority=9)
            await asyncio.sleep(1.0)