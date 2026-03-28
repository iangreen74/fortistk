"""Blockchain feature engineering for wallet scoring and risk analysis."""
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import json


@dataclass
class BlockchainFeatures:
    """Container for extracted blockchain features."""
    # Transaction graph metrics
    tx_count: int
    unique_counterparties: int
    avg_tx_value: float
    max_tx_value: float
    total_volume: float
    in_degree: int
    out_degree: int
    clustering_coefficient: float
    
    # Temporal patterns
    first_tx_timestamp: Optional[int]
    last_tx_timestamp: Optional[int]
    account_age_days: float
    tx_frequency: float
    active_days: int
    max_daily_tx_count: int
    time_std_dev: float
    
    # Address characteristics
    is_contract: bool
    balance: float
    unique_tokens: int
    defi_interactions: int
    exchange_interactions: int
    risk_score: float
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_normalized(self) -> Dict[str, float]:
        """Return normalized feature vector."""
        features = self.to_dict()
        normalized = {}
        for key, value in features.items():
            if isinstance(value, (int, float)) and value is not None:
                normalized[key] = float(value)
        return normalized


class FeatureExtractor:
    """Extract and engineer features from blockchain data."""
    
    def __init__(self):
        self.feature_cache: Dict[str, BlockchainFeatures] = {}
    
    def extract_transaction_graph_metrics(self, transactions: List[Dict]) -> Dict[str, float]:
        """Extract graph-based metrics from transaction history."""
        if not transactions:
            return {
                "tx_count": 0,
                "unique_counterparties": 0,
                "avg_tx_value": 0.0,
                "max_tx_value": 0.0,
                "total_volume": 0.0,
                "in_degree": 0,
                "out_degree": 0,
                "clustering_coefficient": 0.0
            }
        
        values = [float(tx.get("value", 0)) for tx in transactions]
        from_addrs = set(tx.get("from") for tx in transactions if tx.get("from"))
        to_addrs = set(tx.get("to") for tx in transactions if tx.get("to"))
        
        return {
            "tx_count": len(transactions),
            "unique_counterparties": len(from_addrs | to_addrs),
            "avg_tx_value": np.mean(values) if values else 0.0,
            "max_tx_value": max(values) if values else 0.0,
            "total_volume": sum(values),
            "in_degree": len(from_addrs),
            "out_degree": len(to_addrs),
            "clustering_coefficient": self._calculate_clustering(transactions)
        }
    
    def extract_temporal_patterns(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Extract time-based patterns from transactions."""
        if not transactions:
            return {
                "first_tx_timestamp": None,
                "last_tx_timestamp": None,
                "account_age_days": 0.0,
                "tx_frequency": 0.0,
                "active_days": 0,
                "max_daily_tx_count": 0,
                "time_std_dev": 0.0
            }
        
        timestamps = [int(tx.get("timestamp", 0)) for tx in transactions if tx.get("timestamp")]
        if not timestamps:
            timestamps = [int(datetime.now().timestamp())]
        
        timestamps.sort()
        first_ts, last_ts = timestamps[0], timestamps[-1]
        age_seconds = last_ts - first_ts
        age_days = age_seconds / 86400 if age_seconds > 0 else 0.001
        
        daily_counts = {}
        for ts in timestamps:
            day = ts // 86400
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        return {
            "first_tx_timestamp": first_ts,
            "last_tx_timestamp": last_ts,
            "account_age_days": age_days,
            "tx_frequency": len(timestamps) / age_days,
            "active_days": len(daily_counts),
            "max_daily_tx_count": max(daily_counts.values()) if daily_counts else 0,
            "time_std_dev": float(np.std(timestamps)) if len(timestamps) > 1 else 0.0
        }
    
    def extract_address_characteristics(self, address_data: Dict) -> Dict[str, Any]:
        """Extract address-specific characteristics."""
        return {
            "is_contract": address_data.get("is_contract", False),
            "balance": float(address_data.get("balance", 0)),
            "unique_tokens": len(address_data.get("tokens", [])),
            "defi_interactions": address_data.get("defi_count", 0),
            "exchange_interactions": address_data.get("exchange_count", 0),
            "risk_score": float(address_data.get("risk_score", 0.5))
        }
    
    def extract_features(self, wallet_data: Dict) -> BlockchainFeatures:
        """Extract all features from wallet data."""
        transactions = wallet_data.get("transactions", [])
        address_data = wallet_data.get("address_info", {})
        
        graph_metrics = self.extract_transaction_graph_metrics(transactions)
        temporal_patterns = self.extract_temporal_patterns(transactions)
        address_chars = self.extract_address_characteristics(address_data)
        
        features = BlockchainFeatures(
            **graph_metrics,
            **temporal_patterns,
            **address_chars
        )
        
        # Cache features
        wallet_id = wallet_data.get("address", "unknown")
        self.feature_cache[wallet_id] = features
        
        return features
    
    def _calculate_clustering(self, transactions: List[Dict]) -> float:
        """Calculate clustering coefficient for transaction graph."""
        if len(transactions) < 2:
            return 0.0
        edges = [(tx.get("from"), tx.get("to")) for tx in transactions]
        edges = [(f, t) for f, t in edges if f and t]
        if not edges:
            return 0.0
        return min(1.0, len(set(edges)) / len(edges))
