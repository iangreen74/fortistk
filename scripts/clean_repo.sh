#!/bin/bash

set -e

echo "🚀 Moving all useful scripts to root /scripts/..."

# Move scripts from infra/scripts to root scripts
mv infra/scripts/bootstrap_backend.sh scripts/
mv infra/scripts/deploy.sh scripts/
mv infra/scripts/push_to_ecr.tf scripts/push_to_ecr.sh

echo "🧹 Removing old /infra/scripts folder..."
rm -rf infra/scripts

echo "🔧 Fixing IAM module typo (maint.tf → main.tf)..."
mv infra/modules/iam/maint.tf infra/modules/iam/main.tf

echo "🧹 Cleaning up unneeded dummy README.md files..."

# Remove redundant or placeholder READMEs in subfolders
rm -f agents/base_agent/README.md
rm -f agents/wallet_score_agent/model/README.md
rm -f ai/README.md
rm -f ai/models/README.md
rm -f ai/models/gambling_risk_model/README.md
rm -f ai/models/tx_graph_model/README.md
rm -f ai/utils/README.md
rm -f backend/fastapi_service/README.md
rm -f backend/fastapi_service/api/README.md
rm -f cli/README.md
rm -f data/README.md
rm -f data/examples/README.md
rm -f data/schemas/README.md
rm -f data/training_data/README.md
rm -f infra/envs/README.md
rm -f infra/envs/dev/README.md
rm -f infra/envs/prod/README.md
rm -f infra/modules/README.md
rm -f infra/modules/agent_gateway/README.md
rm -f infra/modules/agent_runtime/README.md
rm -f infra/modules/alb/README.md
rm -f infra/modules/ecr/README.md
rm -f infra/modules/ecs_cluster/README.md
rm -f infra/modules/monitoring/README.md
rm -f infra/modules/swarm_scaler/README.md
rm -f infra/modules/vpc/README.md

echo "🧹 Deleting invalid push_to_ecr Terraform file (was misnamed)..."
rm -f scripts/push_to_ecr.tf

echo "🔧 (Optional) Renaming validate.yaml to validate.yml for consistency..."
mv .github/workflows/validate.yaml .github/workflows/validate.yml

echo "✅ Repository structure has been cleaned and polished!"
