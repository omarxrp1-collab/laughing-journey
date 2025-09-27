from .base_agent import BaseAgent
import time
from collections import deque

class PerformanceMetricsAgent(BaseAgent):
    def __init__(self, name, bus, cfg):
        super().__init__(name, bus, ["POSITION_CLOSED","EXEC_STATUS"])
        self.cfg = cfg
        self.equity = cfg["general"]["base_equity"]
        self.max_equity = self.equity
        self.closed = 0
        self.win = 0
        self.brier_list = deque(maxlen=1000)

    async def handle(self, msg):
        if msg.type == "POSITION_CLOSED":
            pnl = msg.payload.get("pnl_dollar",0)
            prob = msg.payload.get("prob")
            outcome = 1 if pnl > 0 else 0
            self.equity += pnl
            self.max_equity = max(self.max_equity, self.equity)
            self.closed += 1
            if outcome == 1: self.win += 1
            if prob is not None:
                self.brier_list.append((prob - outcome)**2)
            if self.closed % 20 == 0:
                dd = (self.max_equity - self.equity)/self.max_equity if self.max_equity>0 else 0
                brier = sum(self.brier_list)/len(self.brier_list) if self.brier_list else None
                await self.publish("PERFORMANCE_METRICS", {
                    "closed_trades": self.closed,
                    "win_rate": self.win / self.closed,
                    "drawdown_pct": dd,
                    "equity": self.equity,
                    "brier": brier
                }, priority=1)