import pytest
from guardian.ml_engine import MLEngine
from guardian.models import CloudPricing, CloudProvider

@pytest.mark.asyncio
async def test_ml_engine_initialization():
    engine = MLEngine()
    assert engine is not None
    assert engine.is_trained == False

@pytest.mark.asyncio
async def test_training_and_prediction():
    engine = MLEngine()
    await engine.train()
    assert engine.is_trained == True
    
    candidates = [
        CloudPricing(provider=CloudProvider.AWS, region="us-east-1", instance_type="m5.large", price_on_demand=0.096, price_spot=0.035)
    ]
    
    predictions = await engine.predict(2.0, 4.0, candidates)
    assert len(predictions) == 1
    assert predictions[0].predicted_cost > 0
    assert predictions[0].predicted_latency > 0

