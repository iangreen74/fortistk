# FortiSTK Repository Architecture

## 🌐 Vision

FortiSTK is a **modular, self-replicating security mesh for Web3 gambling fraud detection**, powered by distributed AI agents and designed with antifragility and automation at its core. The system is engineered to evolve, scale, and defend autonomously.

## ✅ Core Engineering Principles

- **Swarm Intelligence**: Each agent is an autonomous AI unit that can analyze, score, and report independently, yet operate in coordination.
- **Antifragile Infrastructure**: Errors are logged, services restart automatically, monitoring is built-in. Stress improves the system.
- **Immutable Region**: All infrastructure is permanently deployed to `us-east-1`. This does not change.
- **Automation-First**: Single-developer optimized. GitHub Actions, Makefiles, and scripts power CI/CD and replication.
- **Open Core**: Public GitHub repo with core system exposed, premium swarm coordinator logic gated.

## 🧱 Repo Layout

```text
fortistk/
├── README.md                    # Project overview
├── REPO_ARCHITECTURE.md        # This document
├── infra/                      # All Terraform infrastructure
│   ├── envs/                   # Environment-specific deployments (dev, prod)
│   │   └── dev/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       ├── terraform.tfvars
│   │       └── backend.tf
│   ├── modules/                # Reusable infra modules
│   │   ├── vpc/
│   │   ├── ecs_cluster/
│   │   ├── agent_runtime/
│   │   ├── agent_gateway/
│   │   ├── swarm_scaler/
│   │   └── monitoring/
│   └── scripts/                # Deployment helpers
│       └── deploy.sh
├── agents/                     # AI swarm agents
│   ├── base_agent/             # Abstract interface
│   ├── wallet_score_agent/     # Example agent (deployed first)
│   ├── gambling_detector/
│   └── tx_graph_agent/
├── backend/                    # Control node FastAPI service
│   └── fastapi_service/
│       ├── main.py
│       ├── requirements.txt
│       └── api/
│           ├── routes.py
│           └── schemas.py
├── cli/                        # CLI tools
│   └── analyze_wallet.py
├── data/                       # Data schemas, examples, training sets
│   ├── schemas/
│   ├── examples/
│   └── training_data/
├── ai/                         # ML models and utilities
│   ├── models/
│   │   ├── gambling_risk_model/
│   │   └── tx_graph_model/
│   └── utils/
│       └── feature_extraction.py
├── scripts/                    # Automation + agent scaffolding
│   ├── run_all_agents.sh
│   ├── bootstrap_agent.sh
│   └── make_agent.py
└── .github/
    └── workflows/
        └── deploy.yml
```

## 🛠 Change Rules

- All changes to infra or AI logic must align with swarm-agent modularity.
- No direct region references outside of `terraform.tfvars` or protected `backend.tf`.
- New agents must implement the `BaseAgent` interface.
- All modules must be testable and independently deployable.

## 🔐 Public vs Private

This repo is public, showing the core system and agent architecture. The swarm coordination logic may be commercialized or gated via SaaS licensing.

## 🧠 Deployment Lifecycle

- Run `init_repo_structure.sh` to scaffold
- Use `deploy.sh dev` to provision core infra
- Use `make_agent.py` to scaffold and deploy new agents
- CI/CD triggers automatic formatting, plan checks, deploy gates

## 🚧 Future Enhancements

- Agent discovery via decentralized DNS
- On-chain intelligence feedback loop
- Agent reputation system for consensus-based fraud detection
