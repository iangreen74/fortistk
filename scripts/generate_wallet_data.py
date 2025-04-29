# scripts/generate_wallet_data.py

import pandas as pd
import numpy as np
import os

def generate_wallet_data(samples=1000, output_path="agents/wallet_score_agent/data/wallet_data.csv"):
    np.random.seed(42)

    data = {
        "tx_volume": np.random.exponential(scale=5000, size=samples),
        "avg_tx_amount": np.random.normal(loc=200, scale=50, size=samples),
        "num_unique_counterparties": np.random.poisson(lam=10, size=samples),
        "new_wallet_flag": np.random.binomial(1, 0.2, size=samples),
        "is_contract": np.random.binomial(1, 0.1, size=samples),
        "avg_gas_price": np.random.normal(loc=50, scale=15, size=samples)
    }

    df = pd.DataFrame(data)

    # Introduce label with simple logic
    df["label"] = (
        (df["tx_volume"] > 10000) | 
        (df["new_wallet_flag"] == 1) & (df["avg_gas_price"] > 70)
    ).astype(int)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Generated {samples} samples -> {output_path}")


if __name__ == "__main__":
    generate_wallet_data()
