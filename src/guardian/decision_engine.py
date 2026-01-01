import logging
from typing import List, Optional
from guardian.models import (
    WorkloadCurrentState, 
    PlacementOption, 
    WorkloadPlacementPolicy, 
    PlacementRecommendation
)

logger = logging.getLogger(__name__)

class DecisionEngine:
    def __init__(self):
        logger.info("DecisionEngine initialized")

    async def generate_recommendation(
        self, 
        current_state: WorkloadCurrentState, 
        options: List[PlacementOption], 
        policy: WorkloadPlacementPolicy
    ) -> Optional[PlacementRecommendation]:
        """
        Evaluate options against the policy and current state to recommend a migration.
        Returns None if staying put is the best option or no option meets criteria.
        """
        logger.info(f"Evaluating {len(options)} placement options for {current_state.workload_name}")
        
        best_option: Optional[PlacementOption] = None
        max_score = -1.0
        
        # Calculate current utility score
        current_score = self._calculate_score(
            current_state.current_cost, 
            current_state.current_latency, 
            policy
        )
        
        valid_options = []
        
        for option in options:
            # 1. Compliance Check
            if option.cloud not in policy.allowed_clouds:
                continue
                
            # 2. Latency Constraint Check
            if option.predicted_latency > policy.max_latency_ms:
                continue
            
            score = self._calculate_score(option.predicted_cost, option.predicted_latency, policy)
            
            if score > max_score:
                max_score = score
                best_option = option
                
        if not best_option:
            logger.info("No valid placement options found matching policy constraints.")
            return None
            
        # 3. Improvement Threshold Check
        # Does the best option offer enough savings?
        estimated_savings = current_state.current_cost - best_option.predicted_cost
        savings_percent = estimated_savings / current_state.current_cost if current_state.current_cost > 0 else 0
        
        logger.info(f"Best option: {best_option.cloud}/{best_option.region}. Savings: {savings_percent:.1%}")
        
        if savings_percent >= policy.savings_threshold:
             return PlacementRecommendation(
                 workload_name=current_state.workload_name,
                 namespace=current_state.namespace,
                 current_state=current_state,
                 recommended_option=best_option,
                 estimated_savings=round(estimated_savings, 2)
             )
        
        # Also migrate if latency is significantly better? (Optional logic extension)
        
        return None

    def _calculate_score(self, cost: float, latency: float, policy: WorkloadPlacementPolicy) -> float:
        """
        Calculate a utility score (higher is better).
        Simple weighted sum interpretation: minimize cost and latency.
        Inverted so higher is better.
        """
        # Normalize (rough heuristics)
        norm_cost = cost / 100.0 # Assume $100 is "high" daily cost reference
        norm_latency = latency / 100.0 # Assume 100ms is "high" latency
        
        # Score = 100 - (Weighted Cost + Weighted Latency)
        # We want to MINIMIZE the weighted sum.
        penalty = (policy.cost_weight * norm_cost) + (policy.latency_weight * norm_latency)
        return 1000.0 - penalty

