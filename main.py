import asyncio, yaml
from engine.event_bus import EventBus
from engine.orchestrator import Orchestrator

from engine.agents.data_agent import DataAgent
from engine.agents.feature_agent import FeatureAgent
from engine.agents.regime_agent import RegimeAgent
from engine.agents.signal_agent import SignalAgent
from engine.agents.eae_agent import EAEAgent
from engine.agents.stop_target_agent import StopTargetAgent
from engine.agents.risk_agent import RiskAgent
from engine.agents.execution_agent import ExecutionAgent
from engine.agents.trail_agent import TrailAgent
from engine.agents.performance_metrics_agent import PerformanceMetricsAgent
from engine.agents.drift_agent import DriftAgent
from engine.agents.governance_agent import GovernanceAgent
from engine.agents.logging_agent import LoggingAgent
from engine.agents.universe_agent import UniverseAgent

class DummyExchangeMeta:
    async def list_symbols(self):
        # نموذج مبدئي – استبدل بمصدر حقيقي لاحقاً
        base = ["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","ADAUSDT","LTCUSDT"]
        out = []
        import random
        for s in base:
            out.append({
                "symbol": s,
                "volume_24h": random.randint(5_000_000,150_000_000),
                "spread": random.uniform(0.0004,0.0015),
                "funding": random.uniform(-0.01,0.01)
            })
        return out

class DummyModel:
    def predict(self, X): return ["MEAN_REV"]*len(X)

async def main():
    with open("config/agents.yaml","r") as f:
        cfg = yaml.safe_load(f)
    bus = EventBus()
    regime_model = DummyModel()
    exchange_meta = DummyExchangeMeta()

    agents = {
        "UniverseAgent": UniverseAgent("UniverseAgent", bus, cfg, exchange_meta),
        "DataAgent": DataAgent("DataAgent", bus, cfg["general"]["symbols_initial"]),
        "FeatureAgent": FeatureAgent("FeatureAgent", bus, cfg),
        "RegimeAgent": RegimeAgent("RegimeAgent", bus, regime_model),
        "SignalAgent": SignalAgent("SignalAgent", bus, cfg),
        "EAEAgent": EAEAgent("EAEAgent", bus),
        "StopTargetAgent": StopTargetAgent("StopTargetAgent", bus, cfg),
        "RiskAgent": RiskAgent("RiskAgent", bus, cfg),
        "ExecutionAgent": ExecutionAgent("ExecutionAgent", bus, cfg),
        "TrailAgent": TrailAgent("TrailAgent", bus, cfg),
        "PerformanceMetricsAgent": PerformanceMetricsAgent("PerformanceMetricsAgent", bus, cfg),
        "DriftAgent": DriftAgent("DriftAgent", bus, cfg),
        "GovernanceAgent": GovernanceAgent("GovernanceAgent", bus, cfg),
        "LoggingAgent": LoggingAgent("LoggingAgent", bus)
    }

    orchestrator = Orchestrator(agents)
    await orchestration_start(bus, agents, orchestrator)

async def orchestration_start(bus, agents, orchestrator):
    tasks = [asyncio.create_task(agents["UniverseAgent"].run()),
             asyncio.create_task(orchestrator.start(bus))]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())