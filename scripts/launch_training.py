# Cleaned launcher
from sagemaker.sklearn import SKLearn
import os
import sagemaker

ROLE = os.environ.get("SAGEMAKER_ROLE_ARN")
BUCKET = os.environ.get("SAGEMAKER_BUCKET")
REGION = os.environ.get("AWS_REGION", "us-east-1")

ENTRY_POINT = "train.py"        # ONLY the filename now
SOURCE_DIR = "agents/wallet_score_agent/"   # Full folder to upload
OUTPUT_PATH = f"s3://{BUCKET}/wallet_score_agent/output"
TRAINING_DATA = f"s3://{BUCKET}/wallet_score_agent/data/"

sagemaker_session = sagemaker.Session()

def launch_training():
    estimator = SKLearn(
        entry_point=ENTRY_POINT,
        source_dir=SOURCE_DIR,
        role=ROLE,
        instance_type="ml.m5.large",
        instance_count=1,
        framework_version="0.23-1",
        py_version="py3",
        output_path=OUTPUT_PATH,
        sagemaker_session=sagemaker_session,
        base_job_name="wallet-score-agent-training"
    )

    estimator.fit({"train": TRAINING_DATA})

if __name__ == "__main__":
    launch_training()
