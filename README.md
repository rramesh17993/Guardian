# Guardian: Multi-Cloud Workload Placement Optimizer

Guardian is an intelligent Kubernetes operator that continuously optimizes workload placement across multiple cloud providers (AWS, GCP, Azure). It leverages machine learning to predict cost and performance, automatically migrating workloads to the optimal execution environment.

## The Problem

Organizations today run multi-cloud workloads but lack the intelligence to place them optimally. 

**The scenario:**
- **Monday 10 AM**: AWS spot prices spike 40% in `us-east-1`.
- **Monday 10 AM - Wednesday**: Workloads continue running on AWS, wasting thousands in compute spend.
- **Wednesday 2 PM**: FinOps team notices the spike and manually investigates.
- **Thursday**: Manual migration takes place.

**The Cost**: $10k+ wasted and significant engineering time lost to manual rebalancing.

## The Solution

Guardian treats cloud placement as a continuously optimizable decision. It ingests real-time pricing and performance signals, uses machine learning to predict the best future state, and automates the migration.

- **Automated Savings**: Reduces compute spend by 25-40% through spot instance arbitrage and regional optimization.
- **SLA Protection**: Balances cost savings with latency requirements to ensure performance never suffers.
- **True Multi-Cloud**: Move beyond "multi-cloud visibility" to "multi-cloud execution."

## Quick Start

Get Guardian running in 3 commands:

```bash
# 1. Install CRDs and RBAC
kubectl apply -f deploy/crds/ && kubectl apply -f deploy/rbac.yaml

# 2. Deploy the Operator
kubectl apply -f deploy/operator.yaml

# 3. Apply your first optimization policy
kubectl apply -f examples/cost-optimizer.yaml
```

## Architecture

Guardian operates as a continuous control loop across your multi-cloud inventory.

### Conceptual View

```text
       [ SIGNAL INGESTION ]          [ INTELLIGENCE ]          [ EXECUTION ]
      /                    \        /                \        /             \
AWS  +----------------------+      +------------------+      +---------------+
GCP  |  Metrics Collector   | ---> |    ML Engine     | ---> | Migration     |
AZR  +----------------------+      +------------------+      | Orchestrator  |
      \                    /      /                  \       +---------------+
       [ Latency Probes   ]      [ Decision Engine  ]               |
                                                                    v
                                                     [ TARGET CLOUD CLUSTER ]
```

### Technical Component Flow

```mermaid
graph LR
    subgraph "Signal Ingestion"
        MC[Metrics Collector]
        LP[Latency Probes]
    end

    subgraph "Intelligence (Operator)"
        ML[ML Prediction Engine]
        DE[Decision Engine]
        Policy[Placement Policy]
    end

    subgraph "Multi-Cloud Inventory"
        AWS[AWS Cluster]
        GCP[GCP Cluster]
        AZR[Azure Cluster]
    end

    MC -->|Spot/On-Demand| ML
    LP -->|Regional Latency| ML
    AWS -.->|Workload Telemetry| MC
    GCP -.->|Workload Telemetry| MC
    AZR -.->|Workload Telemetry| MC

    ML -->|Predictions| DE
    Policy --> DE
    
    DE -->|Migration Plan| MO[Migration Orchestrator]
    MO -->|Zero-Downtime Migration| AWS
    MO -->|Zero-Downtime Migration| GCP
    MO -->|Zero-Downtime Migration| AZR
```

## Competitive Positioning

| Feature | Guardian | Karpenter | Kubecost | CAST AI |
|---------|----------|-----------|----------|---------|
| **Scope** | Inter-Cloud | Intra-Cloud | Visibility | SaaS Platform |
| **Logic** | ML-Driven | Rule-based | Reporting | Proprietary |
| **Migration** | Zero-downtime | Auto-scaling | Manual | Proprietary |
| **Hosting** | Self-hosted | Self-hosted | Self-hosted | SaaS |

## Roadmap

- [x] **v0.1.0 (MVP)**: Core operator loop, multi-cloud pricing ingestion (AWS/Azure/GCP).
- [x] **Intelligence**: ML-driven prediction models and multi-objective optimization.
- [x] **Autonomous Execution**: Migration orchestration with health validation and simulation.
- [ ] **v0.2.0**: Advanced GitOps integration with cluster-api for automated provisioning.
- [ ] **Real-world Migration**: Plug-in drivers for Velociraptor or Velero for stateful migration.
- [ ] **Reinforcement Learning**: Transition from Random Forest to RL for dynamic placement.

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

---
*Built by Rajesh Ramesh.*
