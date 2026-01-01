import logging
import numpy as np
import pandas as pd
from typing import List, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from guardian.models import CloudPricing, PlacementOption, CloudProvider

logger = logging.getLogger(__name__)

class MLEngine:
    def __init__(self):
        # We predict (cost, latency)
        self.model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
        self.is_trained = False
        logger.info("MLEngine initialized")

    async def train(self):
        """
        Train the model on synthetic historical data.
        In production, this would load from a database or Feature Store.
        """
        logger.info("Training ML model on synthetic data...")
        
        # Synthetic Feature Engineering
        # Features: [cpu_cores, memory_gb, provider_idx, region_idx]
        # Targets: [cost, latency]
        
        # 0: AWS, 1: GCP, 2: Azure/Other
        X_train = np.array([
            [2, 4, 0, 0], [2, 4, 0, 1], [2, 4, 1, 0],  # Small workloads
            [4, 16, 0, 0], [4, 16, 1, 0], [4, 16, 2, 0], # Medium workloads
            [16, 64, 0, 0], [16, 64, 1, 0],             # Large workloads
        ])
        
        # Cost ($/day), Latency (ms)
        y_train = np.array([
            [2.4, 30], [2.5, 90], [2.2, 35],
            [12.0, 30], [10.5, 38], [13.0, 40],
            [55.0, 30], [48.0, 42]
        ])
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        logger.info("ML model training complete")

    async def predict(self, cpu_cores: float, memory_gb: float, candidates: List[CloudPricing]) -> List[PlacementOption]:
        """
        Predict cost and latency for a list of candidate cloud environments.
        """
        if not self.is_trained:
            await self.train()
            
        results = []
        
        for candidate in candidates:
            # Simple feature encoding
            provider_idx = 0 if candidate.provider == CloudProvider.AWS else (1 if candidate.provider == CloudProvider.GCP else 2)
            # Mock region encoding
            region_idx = 0 
            
            features = np.array([[cpu_cores, memory_gb, provider_idx, region_idx]])
            
            prediction = self.model.predict(features)[0]
            predicted_cost = round(max(0.0, prediction[0]), 2) # Ensure positive
            predicted_latency = round(max(0.0, prediction[1]), 1)
            
            # Confidence score (mocked based on n_estimators variance or distance)
            confidence = 0.85 + (0.10 * np.random.random()) # 0.85 - 0.95
            
            results.append(PlacementOption(
                cloud=candidate.provider,
                region=candidate.region,
                predicted_cost=predicted_cost,
                predicted_latency=predicted_latency,
                confidence_score=round(confidence, 2)
            ))
            
        return results

