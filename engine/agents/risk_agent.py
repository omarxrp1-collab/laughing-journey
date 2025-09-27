from .base_agent import BaseAgent
import time

class RiskAgent(BaseAgent):
    """يحوّل خطة الوقف والأهداف إلى حجم صفقة بمخاطرة ثابتة 1% (fixed_risk_pct)."""
    def __init__(self, name, bus, cfg):
        super().__init__(name, bus, ["STOP_TARGET_PLAN","RISK_DECISION"])
        self.cfg = cfg
        self.equity = cfg["general"]["base_equity"]
        self.pending = {}  # symbol -> stop_plan
        self.positions_open = 0
        self.symbol_last_loss = {}
        self.symbol_cooldown_min = cfg["risk"].get("per_symbol_cooldown_min", 5)

    async def handle(self, msg):
        if msg.type == "STOP_TARGET_PLAN":
            if not msg.payload.get("valid", True):
                return
            self.pending[msg.symbol] = msg.payload
            await self._finalize(msg.symbol)
        elif msg.type == "RISK_DECISION":
            # في وضع المخاطرة الثابتة يمكن تجاهلها أو استخدامها لاحقاً لمعلومات إضافية
            pass

    def _symbol_on_cooldown(self, symbol):
        last = self.symbol_last_loss.get(symbol, 0)
        return (time.time() - last) < self.symbol_cooldown_min * 60

    async def _finalize(self, symbol):
        if self.positions_open >= self.cfg["risk"]["max_positions"]:
            return
        plan = self.pending.get(symbol)
        if not plan:
            return
        # حساب المسافة
        entry = plan["entry_price"]
        stop = plan["stop_price"]
        stop_dist_pct = abs(entry - stop) / entry
        if stop_dist_pct < self.cfg["risk"]["min_stop_pct"]:
            return
        if stop_dist_pct > self.cfg["risk"]["max_stop_pct"]:
            if self.cfg["risk"].get("reject_if_stop_out_of_range", True):
                return
        risk_pct = self.cfg["risk"]["fixed_risk_pct"]
        risk_dollar = self.equity * risk_pct
        notional = risk_dollar / max(stop_dist_pct, 1e-9)
        quantity = notional / entry
        # تحقق R الأول
        first_target = plan["targets"][0]
        reward_abs = abs(first_target - entry)
        risk_abs = abs(entry - stop)
        R_first = reward_abs / max(risk_abs,1e-9)
        if R_first < self.cfg["thresholds"]["min_r_expectancy"]:
            return
        self.positions_open += 1
        await self.publish("POSITION_PLAN", {
            "direction": plan["direction"],
            "entry_price": entry,
            "stop_price": stop,
            "targets": plan["targets"],
            "prob": plan.get("prob"),
            "risk_pct": risk_pct,
            "risk_dollar": risk_dollar,
            "quantity": quantity
        }, symbol=symbol, priority=2)