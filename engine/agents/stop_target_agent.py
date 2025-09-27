from .base_agent import BaseAgent

class StopTargetAgent(BaseAgent):
    def __init__(self, name, bus, cfg):
        super().__init__(name, bus, ["MAE_ESTIMATE"])
        self.cfg = cfg

    async def handle(self, msg):
        p = msg.payload
        feats = p["features"]
        price = feats["close"]
        atr = feats.get("atr") or (price * 0.0015)
        direction = p["direction"]
        dev = feats.get("dev_ema50_atr", 0)
        vol_state = abs(dev)
        if vol_state > 2.2:
            atr_mult = self.cfg["stops_targets"]["volatile_atr_mult"]
            multipliers = self.cfg["stops_targets"]["tp_multipliers_high_vol"]
        elif vol_state < 1.0:
            atr_mult = self.cfg["stops_targets"]["calm_atr_mult"]
            multipliers = self.cfg["stops_targets"]["tp_multipliers_low_vol"]
        else:
            atr_mult = self.cfg["stops_targets"]["base_atr_mult"]
            multipliers = self.cfg["stops_targets"]["tp_multipliers_mid_vol"]
        raw_dist = atr_mult * atr
        min_stop = self.cfg["risk"]["min_stop_pct"] * price
        max_stop = self.cfg["risk"]["max_stop_pct"] * price
        dist = max(min_stop, min(raw_dist, max_stop))
        if direction == "LONG":
            stop_price = price - dist
            risk_unit = price - stop_price
        else:
            stop_price = price + dist
            risk_unit = stop_price - price
        targets = []
        for m in multipliers:
            if direction == "LONG":
                targets.append(price + m * risk_unit)
            else:
                targets.append(price - m * risk_unit)
        await self.publish("STOP_TARGET_PLAN", {
            "direction": direction,
            "prob": p["prob"],
            "entry_price": price,
            "stop_price": stop_price,
            "risk_unit": risk_unit,
            "targets": targets,
            "valid": True
        }, symbol=msg.symbol, priority=4)