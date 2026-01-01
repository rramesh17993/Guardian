from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class CloudProvider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"

class MetricType(str, Enum):
    COST = "cost"
    LATENCY = "latency"
    CPU = "cpu"
    MEMORY = "memory"

class CloudPricing(BaseModel):
    provider: CloudProvider
    region: str
    instance_type: str
    price_on_demand: float
    price_spot: float
    currency: str = "USD"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WorkloadCurrentState(BaseModel):
    workload_name: str
    namespace: str
    current_cloud: CloudProvider
    current_region: str
    current_cost: float
    current_latency: float

class PlacementOption(BaseModel):
    cloud: CloudProvider
    region: str
    predicted_cost: float
    predicted_latency: float
    confidence_score: float

class PlacementRecommendation(BaseModel):
    workload_name: str
    namespace: str
    current_state: WorkloadCurrentState
    recommended_option: PlacementOption
    estimated_savings: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WorkloadPlacementPolicy(BaseModel):
    workload_selector: Dict[str, str]
    cost_weight: int = 40
    latency_weight: int = 40
    compliance_weight: int = 20
    savings_threshold: float = 0.20
    max_latency_ms: int = 100
    allowed_clouds: List[CloudProvider] = [CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE]

