#!/bin/bash

set -e

cd "$(dirname "$0")/../infra/envs/dev"

echo "📦 Initializing Terraform..."
terraform init || exit 1

echo "🧠 Planning Infrastructure Changes..."
terraform plan -var-file=terraform.tfvars || exit 1

echo "🚀 Applying Infrastructure..."
terraform apply -var-file=terraform.tfvars -auto-approve || exit 1

echo "✅ Infrastructure deployed."

echo ""
echo "🔁 If your Docker image is not yet pushed, do this:"
echo "   ./scripts/push_to_ecr.sh"
echo ""
echo "🧠 Reminder: update terraform.tfvars with real security group + target group ARNs if needed."
