# scripts/launch_deployment.py

import boto3
import sagemaker
from sagemaker.sklearn.model import SKLearnModel
import os

# Configuration (edit as needed)
ROLE = os.environ.get("SAGEMAKER_ROLE_ARN")
BUCKET = os.environ.get("SAGEMAKER_BUCKET")
REGION = os.environ.get("AWS_REGION", "us-east-1")

MODEL_ARTIFACT_PATH = f"s3://{BUCKET}/wallet_score_agent/output/{'model.tar.gz'}"  # Standard SageMaker output
ENTRY_POINT = "serve.py"    # Serving script inside the model container
SOURCE_DIR = "agents/wallet_score_agent/"  # Code directory
ENDPOINT_NAME = "wallet-score-agent-endpoint"
INSTANCE_TYPE = "ml.m5.large"

sagemaker_session = sagemaker.Session()


def deploy_model():
    sklearn_model = SKLearnModel(
        model_data=MODEL_ARTIFACT_PATH,
        role=ROLE,
        entry_point=ENTRY_POINT,
        source_dir=SOURCE_DIR,
        framework_version="0.23-1",
        sagemaker_session=sagemaker_session,
        py_version="py3"
    )

    predictor = sklearn_model.deploy(
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
        endpoint_name=ENDPOINT_NAME
    )

    print(f"✅ Deployment complete. Endpoint: {ENDPOINT_NAME}")


if __name__ == "__main__":
    deploy_model()
