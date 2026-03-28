import pytest
from datetime import datetime, timedelta
from main import TransactionAnalyzerAgent


@pytest.fixture
def agent():
    return TransactionAnalyzerAgent()


@pytest.fixture
def sample_transactions():
    base_time = datetime.now().timestamp()
    return [
        {"from": "0xaaa", "to": "0xwallet", "value": 100, "timestamp": base_time, "hash": "0xhash1"},
        {"from": "0xwallet", "to": "0xbbb", "value": 50, "timestamp": base_time + 100, "hash": "0xhash2"},
        {"from": "0xccc", "to": "0xwallet", "value": 200, "timestamp": base_time + 200, "hash": "0xhash3"},
        {"from": "0xwallet", "to": "0xbbb", "value": 30, "timestamp": base_time + 300, "hash": "0xhash4"},
        {"from": "0xbbb", "to": "0xwallet", "value": 150, "timestamp": base_time + 400, "hash": "0xhash5"},
    ]


def test_analyze_requires_wallet_address(agent):
    result = agent.analyze({})
    assert "error" in result


def test_analyze_basic_flow(agent, sample_transactions):
    result = agent.analyze({
        "wallet_address": "0xwallet",
        "transactions": sample_transactions
    })
    assert "flow_analysis" in result
    assert "entity_clusters" in result
    assert "anomalies" in result
    assert "risk_score" in result
    assert result["wallet_address"] == "0xwallet"
    assert result["transaction_count"] == 5


def test_transaction_flow_analysis(agent, sample_transactions):
    flow = agent._analyze_transaction_flow(sample_transactions, "0xwallet")
    assert flow["inflow"]["count"] == 3
    assert flow["outflow"]["count"] == 2
    assert flow["inflow"]["total_value"] == 450
    assert flow["outflow"]["total_value"] == 80
    assert flow["net_flow"] == 370


def test_entity_clustering(agent):
    transactions = [
        {"from": "0xwallet", "to": "0xbbb", "value": 10, "timestamp": 0, "hash": f"0xhash{i}"}
        for i in range(6)
    ]
    clusters = agent._detect_entity_clusters(transactions, "0xwallet")
    assert clusters["cluster_count"] == 1
    assert clusters["clusters"][0]["address"] == "0xbbb"
    assert clusters["clusters"][0]["interaction_count"] == 6


def test_volume_anomaly_detection(agent):
    transactions = [
        {"from": "0xaaa", "to": "0xwallet", "value": 100, "timestamp": 0, "hash": "0xhash1"},
        {"from": "0xbbb", "to": "0xwallet", "value": 20000, "timestamp": 100, "hash": "0xhash2"},
    ]
    anomalies = agent._detect_anomalies(transactions)
    assert anomalies["detected"] is True
    assert len(anomalies["volume"]) >= 1


def test_velocity_anomaly_detection(agent):
    base_time = datetime.now().timestamp()
    transactions = [
        {"from": "0xaaa", "to": "0xwallet", "value": 100, "timestamp": base_time + i, "hash": f"0xhash{i}"}
        for i in range(60)
    ]
    anomalies = agent._detect_anomalies(transactions)
    assert anomalies["detected"] is True
    assert len(anomalies["velocity"]) >= 1


def test_risk_score_calculation(agent):
    flow = {"net_flow": 150000}
    clusters = {"cluster_count": 12}
    anomalies = {"detected": True, "volume": [{}], "velocity": [{}]}
    score = agent._calculate_risk_score(flow, clusters, anomalies)
    assert 0 <= score <= 100
    assert score > 50


def test_risk_level_categorization(agent):
    assert agent._get_risk_level(80) == "high"
    assert agent._get_risk_level(50) == "medium"
    assert agent._get_risk_level(20) == "low"


def test_health_check(agent):
    health = agent.health()
    assert health["status"] == "ok"
    assert "agent" in health
