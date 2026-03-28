"""Unit tests for feature extraction."""
import pytest
from ai.utils.feature_extraction import FeatureExtractor, BlockchainFeatures
from datetime import datetime, timedelta


@pytest.fixture
def feature_extractor():
    return FeatureExtractor()


@pytest.fixture
def sample_transactions():
    base_ts = int(datetime.now().timestamp())
    return [
        {"from": "0xabc", "to": "0xdef", "value": 100, "timestamp": base_ts - 86400 * 10},
        {"from": "0xdef", "to": "0xghi", "value": 200, "timestamp": base_ts - 86400 * 5},
        {"from": "0xghi", "to": "0xabc", "value": 150, "timestamp": base_ts}
    ]


@pytest.fixture
def sample_wallet_data(sample_transactions):
    return {
        "address": "0xabc123",
        "transactions": sample_transactions,
        "address_info": {
            "is_contract": False,
            "balance": 1000.0,
            "tokens": ["TOKEN1", "TOKEN2"],
            "defi_count": 5,
            "exchange_count": 2,
            "risk_score": 0.3
        }
    }


class TestFeatureExtractor:
    def test_extract_transaction_graph_metrics(self, feature_extractor, sample_transactions):
        metrics = feature_extractor.extract_transaction_graph_metrics(sample_transactions)
        
        assert metrics["tx_count"] == 3
        assert metrics["unique_counterparties"] == 3
        assert metrics["avg_tx_value"] == 150.0
        assert metrics["max_tx_value"] == 200.0
        assert metrics["total_volume"] == 450.0
        assert metrics["in_degree"] == 3
        assert metrics["out_degree"] == 3
        assert 0.0 <= metrics["clustering_coefficient"] <= 1.0
    
    def test_extract_temporal_patterns(self, feature_extractor, sample_transactions):
        patterns = feature_extractor.extract_temporal_patterns(sample_transactions)
        
        assert patterns["first_tx_timestamp"] is not None
        assert patterns["last_tx_timestamp"] is not None
        assert patterns["account_age_days"] > 0
        assert patterns["tx_frequency"] > 0
        assert patterns["active_days"] > 0
        assert patterns["max_daily_tx_count"] > 0
        assert patterns["time_std_dev"] >= 0
    
    def test_extract_address_characteristics(self, feature_extractor):
        address_data = {
            "is_contract": True,
            "balance": 5000.0,
            "tokens": ["TOKEN1", "TOKEN2", "TOKEN3"],
            "defi_count": 10,
            "exchange_count": 5,
            "risk_score": 0.7
        }
        
        chars = feature_extractor.extract_address_characteristics(address_data)
        
        assert chars["is_contract"] is True
        assert chars["balance"] == 5000.0
        assert chars["unique_tokens"] == 3
        assert chars["defi_interactions"] == 10
        assert chars["exchange_interactions"] == 5
        assert chars["risk_score"] == 0.7
    
    def test_extract_features_complete(self, feature_extractor, sample_wallet_data):
        features = feature_extractor.extract_features(sample_wallet_data)
        
        assert isinstance(features, BlockchainFeatures)
        assert features.tx_count == 3
        assert features.balance == 1000.0
        assert features.unique_tokens == 2
        assert features.is_contract is False
        
        # Test caching
        assert "0xabc123" in feature_extractor.feature_cache
    
    def test_empty_transactions(self, feature_extractor):
        metrics = feature_extractor.extract_transaction_graph_metrics([])
        assert metrics["tx_count"] == 0
        assert metrics["total_volume"] == 0.0
        
        patterns = feature_extractor.extract_temporal_patterns([])
        assert patterns["account_age_days"] == 0.0
    
    def test_feature_normalization(self, feature_extractor, sample_wallet_data):
        features = feature_extractor.extract_features(sample_wallet_data)
        normalized = features.to_normalized()
        
        assert isinstance(normalized, dict)
        assert all(isinstance(v, float) for v in normalized.values())
        assert "tx_count" in normalized
        assert "balance" in normalized
    
    def test_feature_to_dict(self, feature_extractor, sample_wallet_data):
        features = feature_extractor.extract_features(sample_wallet_data)
        feature_dict = features.to_dict()
        
        assert isinstance(feature_dict, dict)
        assert "tx_count" in feature_dict
        assert "is_contract" in feature_dict
        assert "risk_score" in feature_dict
