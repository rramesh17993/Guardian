import pytest
from guardian.decision_engine import DecisionEngine
from guardian.models import WorkloadCurrentState, PlacementOption, WorkloadPlacementPolicy, CloudProvider

@pytest.mark.asyncio
async def test_recommendation_logic():
    engine = DecisionEngine()
    
    current = WorkloadCurrentState(
        workload_name="test",
        namespace="default",
        current_cloud=CloudProvider.AWS,
        current_region="us-east-1",
        current_cost=10.0,
        current_latency=50.0
    )
    
    # Better option
    option_better = PlacementOption(
        cloud=CloudProvider.GCP,
        region="us-central1",
        predicted_cost=5.0, # 50% savings
        predicted_latency=40.0,
        confidence_score=0.9
    )
    
    policy = WorkloadPlacementPolicy(
        workload_selector={},
        savings_threshold=0.20
    )
    
    rec = await engine.generate_recommendation(current, [option_better], policy)
    
    assert rec is not None
    assert rec.recommended_option.cloud == CloudProvider.GCP
    assert rec.estimated_savings == 5.0

@pytest.mark.asyncio
async def test_no_recommendation_if_savings_low():
    engine = DecisionEngine()
    
    current = WorkloadCurrentState(
        workload_name="test",
        namespace="default",
        current_cloud=CloudProvider.AWS,
        current_region="us-east-1",
        current_cost=10.0,
        current_latency=50.0
    )
    
    # Not enough savings (10%)
    option_meh = PlacementOption(
        cloud=CloudProvider.GCP,
        region="us-central1",
        predicted_cost=9.0, 
        predicted_latency=50.0,
        confidence_score=0.9
    )
    
    policy = WorkloadPlacementPolicy(
        workload_selector={},
        savings_threshold=0.20
    )
    
    rec = await engine.generate_recommendation(current, [option_meh], policy)
    
    assert rec is None
