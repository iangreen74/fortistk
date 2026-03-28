# MLOps Infrastructure

Complete MLOps setup for model training, versioning, deployment, and monitoring.

## Architecture

### 1. Model Registry (S3 + DynamoDB)
- **S3 Bucket**: `{project}-model-registry-{env}`
  - Versioned models stored with metadata
  - Structure: `models/{model_name}/{version}/model.pkl`
  - Artifacts: training data, metrics, configs
- **DynamoDB Table**: Model metadata and lineage
  - Partition key: `model_name`, Sort key: `version`
  - Attributes: training_date, metrics, status, s3_uri

### 2. Experiment Tracking
- **MLflow**: Self-hosted on ECS
  - Backend: PostgreSQL RDS
  - Artifact store: S3
  - UI accessible via ALB
- **Alternative**: Weights & Biases (managed service)

### 3. Training Pipelines
- **SageMaker Training Jobs**: For large-scale training
  - Custom containers with wallet scoring logic
  - Spot instances for cost optimization
- **ECS Tasks**: For lighter training/retraining
  - Scheduled via EventBridge
  - Auto-scaling based on queue depth

### 4. Model Deployment
- **Automated CI/CD**:
  1. Model trained → saved to S3
  2. Model validation tests run
  3. If passing → deploy to staging
  4. Manual approval → production deployment
- **Deployment targets**:
  - SageMaker Endpoints (real-time)
  - Lambda functions (batch)
  - ECS services (custom inference)

### 5. Monitoring
- **Model Drift Detection**:
  - Input drift: Distribution shift in features
  - Prediction drift: Output distribution changes
  - Ground truth monitoring: Compare predictions vs actuals
- **Performance Metrics**:
  - Latency (p50, p95, p99)
  - Throughput (requests/sec)
  - Error rates
  - Model accuracy/precision/recall
- **Alerting**: CloudWatch alarms → SNS → PagerDuty/Slack

## Infrastructure Components

### Terraform Modules
```
ai/mlops/terraform/
├── modules/
│   ├── model_registry/     # S3 + DynamoDB
│   ├── mlflow/             # ECS service + RDS
│   ├── training_pipeline/  # SageMaker + ECS
│   ├── model_serving/      # Inference endpoints
│   └── monitoring/         # CloudWatch + drift detection
└── environments/
    ├── dev/
    ├── staging/
    └── prod/
```

### CI/CD Pipeline
```yaml
# .github/workflows/mlops.yml
1. Code commit → lint (ruff) → test
2. Build Docker images (training, inference)
3. Push to ECR
4. Trigger training job (optional)
5. Deploy model to staging
6. Run integration tests
7. Deploy to production (manual approval)
```

## Usage

### Training a Model
```python
from ai.mlops.training import WalletScoreTrainer

trainer = WalletScoreTrainer(
    experiment_name="wallet-risk-scoring",
    model_name="random-forest-v1"
)
trainer.train(training_data)
trainer.log_metrics({"accuracy": 0.95})
trainer.save_model(s3_path="s3://bucket/models/")
```

### Deploying a Model
```bash
# Via CLI
python -m ai.mlops.deploy \
  --model-name wallet-scorer \
  --version v1.2.0 \
  --environment prod

# Via Terraform
cd ai/mlops/terraform/environments/prod
terraform apply -var="model_version=v1.2.0"
```

### Monitoring
```python
from ai.mlops.monitoring import DriftDetector

detector = DriftDetector(model_name="wallet-scorer")
detector.check_input_drift(recent_data)
detector.check_prediction_drift(predictions)
detector.alert_if_drifted(threshold=0.1)
```

## Setup Instructions

### 1. Deploy Infrastructure
```bash
cd ai/mlops/terraform/environments/dev
terraform init
terraform plan
terraform apply
```

### 2. Configure MLflow
```bash
export MLFLOW_TRACKING_URI=http://mlflow.internal:5000
export MLFLOW_S3_ARTIFACT_ROOT=s3://mlflow-artifacts
```

### 3. Run First Training Job
```bash
python -m ai.mlops.training.train_wallet_scorer \
  --data-path s3://data/wallet-features.parquet \
  --experiment wallet-risk-v1
```

## Model Versioning Strategy
- Semantic versioning: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes in features/output
- MINOR: New features, backward compatible
- PATCH: Bug fixes, retraining on new data

## Drift Detection Strategy
1. **Input Drift**: KS test on feature distributions (daily)
2. **Prediction Drift**: PSI on prediction scores (hourly)
3. **Ground Truth**: Compare predictions vs labels (weekly)
4. **Retraining Trigger**: Drift > threshold for 3 consecutive checks

## Cost Optimization
- Use Spot instances for training (70% savings)
- S3 Intelligent-Tiering for model artifacts
- Auto-scaling inference endpoints
- Delete old experiment artifacts (retention: 90 days)

## Security
- Model artifacts encrypted at rest (S3 SSE)
- IAM roles with least privilege
- VPC endpoints for private connectivity
- Audit logging via CloudTrail

## Troubleshooting
- **Training fails**: Check CloudWatch logs in `/aws/ecs/training-jobs`
- **Deployment stuck**: Verify model artifacts in S3
- **High latency**: Scale inference endpoints or optimize model
- **Drift alerts**: Review feature engineering, consider retraining
