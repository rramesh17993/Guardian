import kopf
import asyncio
import logging
from typing import Dict, Any

from guardian.metrics_collector import MetricsCollector
from guardian.ml_engine import MLEngine
from guardian.decision_engine import DecisionEngine
from guardian.migration_orchestrator import MigrationOrchestrator
from guardian.models import WorkloadPlacementPolicy, CloudProvider

# Global instances
metrics_collector: MetricsCollector = None
ml_engine: MLEngine = None
decision_engine: DecisionEngine = None
migration_orchestrator: MigrationOrchestrator = None

@kopf.on.startup()
async def configure(settings: kopf.OperatorSettings, **_):
    global metrics_collector, ml_engine, decision_engine, migration_orchestrator
    
    settings.posting.level = logging.INFO
    
    metrics_collector = MetricsCollector()
    ml_engine = MLEngine()
    decision_engine = DecisionEngine()
    migration_orchestrator = MigrationOrchestrator()
    
    # Pre-train the model on startup
    await ml_engine.train()
    
    logging.info("Guardian Operator started and components initialized.")

@kopf.timer('guardian.io', 'v1alpha1', 'workloadplacementpolicies', interval=60.0)
async def optimize_placement(spec: Dict[str, Any], status: Dict[str, Any], name: str, namespace: str, **kwargs):
    """
    Periodic optimization loop.
    """
    logging.info(f"Running optimization loop for policy: {name}")
    
    # Adapt spec to model
    try:
        policy = WorkloadPlacementPolicy(
            workload_selector=spec.get('workloadSelector', {}).get('matchLabels', {}),
            cost_weight=spec.get('criteria', {}).get('cost', {}).get('weight', 40),
            latency_weight=spec.get('criteria', {}).get('latency', {}).get('weight', 40),
            compliance_weight= spec.get('criteria', {}).get('compliance', {}).get('weight', 20),
            savings_threshold=spec.get('criteria', {}).get('cost', {}).get('threshold', 0.20),
            max_latency_ms=spec.get('criteria', {}).get('latency', {}).get('maxAcceptable', 100),
            allowed_clouds=[CloudProvider(c) for c in spec.get('criteria', {}).get('compliance', {}).get('allowedClouds', ['aws', 'gcp', 'azure'])]
        )
    except Exception as e:
        logging.error(f"Failed to parse policy {name}: {e}")
        return
    
    # 1. Collect Data
    pricing_data = await metrics_collector.collect_pricing()
    
    # Assume 1 workload matches for this demo
    workload_name = "payment-processor" # In real app, we'd list pods matching selector
    
    current_state = await metrics_collector.get_current_state(workload_name, namespace)
    
    # 2. Predict (ML)
    # Mock resources for the workload
    cpu = 4.0
    mem = 16.0
    
    options = await ml_engine.predict(cpu, mem, pricing_data)
    
    # 3. Decide (Policy)
    recommendation = await decision_engine.generate_recommendation(current_state, options, policy)
    
    if recommendation:
        logging.info(f"Recommendation generated: Move to {recommendation.recommended_option.cloud}")
        
        # 4. Orchestrate (Execute)
        # Check if migration is enabled in status or spec (ignoring for simple demo, assume yes)
        success = await migration_orchestrator.execute_migration(recommendation)
        
        if success:
             return {
                 "lastOptimization": kopf.logger.name,
                 "status": "Migrated",
                 "currentCloud": recommendation.recommended_option.cloud,
                 "savings": recommendation.estimated_savings
             }
    else:
        logging.info(f"No migration recommended for {name}")

    return {
        "lastOptimization": "No change",
        "currentCloud": "aws" # Mock
    }

