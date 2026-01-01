import asyncio
import logging
import random
from typing import List, Dict
from datetime import datetime

from guardian.models import CloudPricing, CloudProvider, WorkloadCurrentState

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.pricing_cache: Dict[str, CloudPricing] = {}
        logger.info("MetricsCollector initialized")

    async def collect_pricing(self) -> List[CloudPricing]:
        """
        Fetch pricing data. Tries real cloud APIs first; falls back to mock if fails (e.g., no credentials).
        """
        logger.info("Collecting cloud pricing data...")
        
        data = []
        try:
            # Attempt to fetch real AWS spot prices
            import boto3
            from botocore.exceptions import NoCredentialsError, ClientError
            
            # Run in thread pool since boto3 is synchronous
            def fetch_aws_spot():
                session = boto3.Session()
                ec2 = session.client('ec2', region_name='us-east-1')
                # Request spot price history for last hour
                response = ec2.describe_spot_price_history(
                    InstanceTypes=['m5.large', 'c5.large', 'p3.2xlarge'],
                    ProductDescriptions=['Linux/UNIX'],
                    StartTime=datetime.utcnow() 
                )
                return response['SpotPriceHistory']

            logger.info("Attempting to connect to AWS API for real-time spot prices...")
            loop = asyncio.get_event_loop()
            history = await loop.run_in_executor(None, fetch_aws_spot)
            
            for item in history:
                # Naive mapping: Use spot price as is, assume on-demand is 3x (mocked) for comparison
                price = float(item['SpotPrice'])
                data.append(CloudPricing(
                    provider=CloudProvider.AWS,
                    region=item['AvailabilityZone'][:-1], # us-east-1a -> us-east-1
                    instance_type=item['InstanceType'],
                    price_on_demand=price * 3.5, # Mock ratio
                    price_spot=price,
                    timestamp=item['Timestamp']
                ))
            
            logger.info(f"Successfully fetched {len(data)} real spot prices from AWS")
            
        except (ImportError, Exception) as e:
            logger.warning(f"Could not fetch real AWS data ({type(e).__name__}: {str(e)}). Using MOCK data.")
            # Fallback to Mock Data
            data = [
                CloudPricing(provider=CloudProvider.AWS, region="us-east-1", instance_type="m5.large", price_on_demand=0.096, price_spot=0.035),
                CloudPricing(provider=CloudProvider.AWS, region="us-west-2", instance_type="m5.large", price_on_demand=0.10, price_spot=0.040),
                CloudPricing(provider=CloudProvider.GCP, region="us-central1", instance_type="e2-standard-2", price_on_demand=0.067, price_spot=0.020),
                CloudPricing(provider=CloudProvider.AZURE, region="eastus", instance_type="D2s_v3", price_on_demand=0.096, price_spot=0.025),
            ]
        
        # Cache results
        for item in data:
            key = f"{item.provider}-{item.region}-{item.instance_type}"
            self.pricing_cache[key] = item
            
        # --- Multi-Cloud Support ---
        # 2. Azure Spot Prices
        try:
            # Azure Retail Prices API (Public, no auth needed for basic price checking, easier for portfolio demo than full SDK auth dance)
            # However, we'll implement a clean request pattern using aiohttp which we already have.
            logger.info("Attempting to fetch Azure Spot prices...")
            import aiohttp
            
            async def fetch_azure_retail():
                url = "https://prices.azure.com/api/retail/prices?currencyCode='USD'&$filter=priceType eq 'Consumption' and (skuName eq 'D2s v3' or skuName eq 'F2s v2')"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            return await resp.json()
                        return None

            azure_data = await fetch_azure_retail()
            if azure_data and 'Items' in azure_data:
                for item in azure_data['Items']:
                    # Azure Retail API returns generic prices, spot is trickier, 
                    # but for this SRE tool we'll treat 'Consumption' as base and mock a discount for spot
                    # since simpler APIs don't always expose dynamic spot rates easily without a sub.
                    base_price = item.get('retailPrice', 0.096)
                    data.append(CloudPricing(
                        provider=CloudProvider.AZURE,
                        region=item.get('location', 'eastus'),
                        instance_type=item.get('skuName', 'D2s_v3'),
                        price_on_demand=base_price,
                        price_spot=base_price * 0.3, # Mock spot discount (Azure Spot is often ~70-90% off)
                        timestamp=datetime.utcnow()
                    ))
                logger.info(f"Fetched {len(azure_data['Items'])} Azure price items")
        except Exception as e:
            logger.warning(f"Could not fetch Azure data: {e}")

        # 3. GCP Spot Prices
        try:
            logger.info("Attempting to fetch GCP machine types...")
            # Using google-cloud-compute to at least verify credentials and list types
            # Spot prices in GCP are static per region/month usually, so listing machine types is the connection check.
            from google.cloud import compute_v1
            
            def fetch_gcp_zones():
                client = compute_v1.ZonesClient()
                request = compute_v1.ListZonesRequest(project="my-project-id", max_results=5) # Will fail if no creds
                return client.list(request=request)

            # verify we can load lib
            # Real GCP pricing extraction usually involves parsing the SKU catalog which is huge.
            # For this tool, we simulate the 'connect' check.
            pass 

        except ImportError:
            pass
        except Exception:
            # Likely 'DefaultCredentialsError', expected in demo env
            logger.warning("GCP Credentials not found, skipping real GCP fetch.")

        return data

    async def measure_latency(self, workload_name: str, target_regions: List[str]) -> Dict[str, float]:
        """
        Simulate measuring latency from the workload to various regions.
        Real impl would use active probing or simple ping checks.
        """
        results = {}
        for region in target_regions:
            # Simulate latency between 20ms and 150ms
            results[region] = round(random.uniform(20.0, 150.0), 1)
        return results

    async def get_current_state(self, workload_name: str, namespace: str) -> WorkloadCurrentState:
        """
        Fetch current state of the workload from K8s.
        """
        # Mock implementation
        return WorkloadCurrentState(
            workload_name=workload_name,
            namespace=namespace,
            current_cloud=CloudProvider.AWS,
            current_region="us-east-1",
            current_cost=2.30, # Daily cost
            current_latency=35.0
        )

