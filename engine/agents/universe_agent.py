from .base_agent import BaseAgent
import time, math

class UniverseAgent(BaseAgent):
    """يجمع ويصنف الرموز إلى Tiers ويحدث قائمة التداول الفعالة."""
    def __init__(self, name, bus, cfg, exchange_meta):
        super().__init__(name, bus, [])
        self.cfg = cfg["universe"]
        self.exchange_meta = exchange_meta
        self.symbol_profiles = {}
        self.last_refresh = 0

    async def run(self):
        while True:
            now = time.time()
            if now - self.last_refresh > self.cfg["refresh_sec"]:
                await self._refresh()
                self.last_refresh = now
            await asyncio.sleep(5)

    async def _refresh(self):
        listings = await self.exchange_meta.list_symbols()
        active = []
        for item in listings:
            sym = item["symbol"]
            if any(ex in sym for ex in self.cfg.get("exclude_patterns", [])):
                continue
            tier = self._classify(item)
            profile = self._build_profile(item, tier)
            self.symbol_profiles[sym] = profile
            if tier != "Tier4":
                active.append(sym)
        active = active[: self.cfg["symbols_limit"]]
        await self.publish("SYMBOLS_UPDATE", {
            "active_symbols": active,
            "profiles": self.symbol_profiles
        }, priority=9)

    def _classify(self, item):
        vol = item.get("volume_24h", 0)
        spread = item.get("spread", 1)
        vth = self.cfg["volume_thresholds"]
        sth = self.cfg["spread_thresholds"]
        if vol >= vth["Tier1"] and spread <= sth["Tier1"]:
            return "Tier1"
        if vol >= vth["Tier2"] and spread <= sth["Tier2"]:
            return "Tier2"
        if vol >= vth["Tier3"] and spread <= sth["Tier3"]:
            return "Tier3"
        return "Tier4"

    def _build_profile(self, item, tier):
        vol = item.get("volume_24h", 0)
        spread = item.get("spread", 0.002)
        vol_norm = math.log10(vol + 1) / 10
        spread_pen = max(0.0, 1 - (spread / 0.003))
        liq_score = max(0.0, min(vol_norm * 0.6 + spread_pen * 0.4, 1.0))
        return {
            "symbol": item["symbol"],
            "tier": tier,
            "liq_score": liq_score,
            "funding": item.get("funding", 0.0),
            "last_eval": time.time()
        }