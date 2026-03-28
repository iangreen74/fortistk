# FortiSTK Repository Architecture

FortiSTK is an open, modular research platform designed to explore the frontiers of distributed AI security for decentralized finance (DeFi) ecosystems.

The repository is organized to support:

- Distributed intelligent agent development.
- Modular AI and machine learning workflows.
- Systematic experiment tracking.
- Scalable model training and deployment.
- Cutting-edge antifragile system design.

---

## Root Structure

| Directory      | Purpose                                                                             |
| :------------- | :---------------------------------------------------------------------------------- |
| `agents/`      | Core AI security agents, each modular and independently deployable.                 |
| `ai/`          | Core AI logic including agent intelligence, utilities, datasets, and MLOps tooling. |
| `models/`      | Saved and versioned trained models for live agent use.                              |
| `training/`    | Training pipelines, scripts, and hyperparameter configs.                            |
| `experiments/` | Research experiments, notebooks, and tracking outputs.                              |
| `artifacts/`   | Saved agent experiences, transaction replays, logs, and other critical artifacts.   |
| `backend/`     | FastAPI backend service coordinating agent communication and external API exposure. |
| `cli/`         | Command-line interface tools for agent orchestration, monitoring, and management.   |
| `infra/`       | Terraform infrastructure modules for scalable deployment.                           |
| `scripts/`     | Bootstrap and automation scripts.                                                   |
| `docs/`        | Technical documentation, mathematical models, and formal research notes.            |

---

## Key Subsystems

### 1. Agents (`/agents/`)

- `base_agent/` — Defines core abstract base classes for FortiSTK agents.
- `wallet_score_agent/` — Initial agent focused on wallet risk profiling.
- `tx_analyzer_agent/` — (Prototype) Agent for transaction anomaly detection.
- `threat_hunter_agent/` — (Prototype) Agent for emergent threat pattern discovery.

Agents operate independently, sharing learned intelligence via decentralized protocols.

### 2. AI Core (`/ai/`)

- `core/` — Intelligence modules (agent brains, memory systems, policy optimizers).
- `utils/` — Support libraries for feature extraction, graph analysis, and data preprocessing.
- `mlops/` — Lightweight tooling for model tracking, dataset versioning, and experiment management.
- `datasets/` — Scripts and tooling to generate synthetic and real-world training data.

### 3. Models (`/models/`)

- Pretrained model artifacts (e.g., Wallet Risk Model v1, Fraud Transaction Model v1).
- Models are versioned and used by agents for live inference.

### 4. Training Pipelines (`/training/`)

- Scripts and configurations to train AI models from scratch or fine-tune existing models.
- Designed to allow fast iterations and reproducibility.

### 5. Experiments (`/experiments/`)

- Research notebooks, experimental results, and analysis.
- Organized for easy reproducibility and peer review.

### 6. Backend (`/backend/`)

- FastAPI-based service layer.
- Exposes APIs for agent coordination, user interaction, and monitoring.

### 7. CLI Tools (`/cli/`)

- Unified CLI tools for local testing, agent orchestration, and system administration.

### 8. Infrastructure (`/infra/`)

- Terraform scripts and modules for scalable cloud deployment (AWS-focused).
- Includes VPC, ECS, ECR, ALB, and monitoring setup.

### 9. Artifacts (`/artifacts/`)

- Agent-generated outputs, replayed transaction histories, logs, and model artifacts.

### 10. Documentation (`/docs/`)

- Formal technical documentation.
- Research papers, architecture blueprints, and mathematical formulations.

---

## Design Principles

- **Modularity** — Every component (agent, model, dataset) is loosely coupled and independently upgradeable.
- **Scalability** — Designed for cloud-native, distributed deployment.
- **Experimentation First** — Optimized for rapid hypothesis testing, research iteration, and learning.
- **Antifragility** — Systems designed to strengthen under attack.
- **Transparency** — Models, agent policies, and experiments are tracked and reproducible.

---

## Future Directions

- Expansion of agent types (fraud hunter, liquidity manipulator detector, governance manipulator monitor).
- Full agent-to-agent secure communication protocols.
- Integration of reinforcement learning for autonomous policy improvement.
- Swarm intelligence-based distributed threat response networks.

---

**FortiSTK — Building the future immune system of decentralized finance.**
