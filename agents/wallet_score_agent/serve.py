# agents/wallet_score_agent/serve.py

import joblib
import os
import pandas as pd
import json

# Load the model when the container starts
model = None

def model_fn(model_dir):
    """
    Load the trained model from the model directory.
    """
    global model
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    return model


def input_fn(request_body, request_content_type):
    """
    Parse the incoming request payload.
    """
    if request_content_type == "application/json":
        input_data = pd.DataFrame(json.loads(request_body))
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")


def predict_fn(input_data, model):
    """
    Apply model to the incoming request.
    """
    prediction = model.predict_proba(input_data)[:, 1]  # Probability of positive class (risk)
    return prediction.tolist()


def output_fn(prediction, response_content_type):
    """
    Format the prediction output.
    """
    if response_content_type == "application/json":
        return json.dumps({"risk_score": prediction})
    else:
        raise ValueError(f"Unsupported response content type: {response_content_type}")
