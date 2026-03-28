# agents/wallet_score_agent/train.py

import argparse
import os
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def model_fn(model_dir):
    """
    Load the trained model for inference.
    """
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    return model


def train(args):
    # Load dataset
    print(f"Loading training data from: {args.data_dir}")
    train_data = pd.read_csv(os.path.join(args.data_dir, "wallet_data.csv"))

    X = train_data.drop("label", axis=1)
    y = train_data["label"]

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define a simple classifier (placeholder: Logistic Regression)
    # Future: Replace with Bayesian updating, GMMs, or more sophisticated models
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Validation Accuracy: {acc:.4f}")

    # Save the model artifact for SageMaker
    path = os.path.join(args.model_dir, "model.joblib")
    print(f"Saving model to: {path}")
    joblib.dump(model, path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # SageMaker-specific arguments. Defaults are set by SageMaker environment.
    parser.add_argument("--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR"))
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--data-dir", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))

    args = parser.parse_args()

    train(args)
