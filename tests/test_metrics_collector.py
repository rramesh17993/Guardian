import pytest
from guardian.metrics_collector import MetricsCollector

@pytest.mark.asyncio
async def test_metrics_collector_initialization():
    collector = MetricsCollector()
    assert collector is not None
    assert collector.pricing_cache == {}

@pytest.mark.asyncio
async def test_collect_pricing():
    collector = MetricsCollector()
    prices = await collector.collect_pricing()
    assert len(prices) > 0
    assert collector.pricing_cache is not None

@pytest.mark.asyncio
async def test_measure_latency():
    collector = MetricsCollector()
    regions = ["us-east-1", "us-west-2"]
    latencies = await collector.measure_latency("test-app", regions)
    assert len(latencies) == 2
    assert "us-east-1" in latencies
    assert "us-west-2" in latencies

