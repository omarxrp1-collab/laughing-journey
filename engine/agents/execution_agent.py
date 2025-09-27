from .base_agent import BaseAgent
import time

class ExecutionAgent(BaseAgent):
    def __init__(self, name, bus, cfg):
        super().__init__(name, bus, ["POSITION_PLAN","AMEND_STOP","FORCE_EXIT"])
        self.cfg = cfg
        self.positions = {}
        self.total_notional = 0

    async def handle(self, msg):
        if msg.type == "POSITION_PLAN":
            await self._open(msg)
        elif msg.type == "AMEND_STOP":
            await self._amend(msg)
        elif msg.type == "FORCE_EXIT":
            await self._close_force(msg)

    async def _open(self, msg):
        p = msg.payload
        symbol = msg.symbol
        # تحقق من الحد الأقصى للتعرض
        notional = p["entry_price"] * p["quantity"]
        equity = self.cfg["general"]["base_equity"]
        if (self.total_notional + notional) / equity > self.cfg["risk"]["max_total_exposure"]:
            return
        # تخزين مباشر (بدون أوامر حقيقية – تكييف لاحقاً للـ API)
        self.positions[symbol] = {
            "entry": p["entry_price"],
            "stop": p["stop_price"],
            "targets": p["targets"],
            "qty": p["quantity"],
            "direction": p["direction"],
            "opened_at": time.time(),
            "prob": p.get("prob"),
            "risk_dollar": p.get("risk_dollar")
        }
        self.total_notional += notional
        await self.publish("EXEC_STATUS", {
            "status": "OPENED",
            "entry": p["entry_price"],
            "stop": p["stop_price"],
            "targets": p["targets"],
            "qty": p["quantity"],
            "prob": p.get("prob")
        }, symbol=symbol, priority=1)

    async def _amend(self, msg):
        if msg.symbol in self.positions:
            self.positions[msg.symbol]["stop"] = msg.payload["new_stop"]
            await self.publish("EXEC_STATUS", {"stop_amended": True, "new_stop": msg.payload["new_stop"]}, symbol=msg.symbol, priority=1)

    async def _close_force(self, msg):
        if msg.symbol in self.positions:
            pos = self.positions.pop(msg.symbol)
            notional = pos["entry"] * pos["qty"]
            self.total_notional -= notional
            await self.publish("POSITION_CLOSED", {"prob": pos.get("prob"), "pnl_dollar": 0}, symbol=msg.symbol, priority=1)