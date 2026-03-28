import pytest
from unittest.mock import patch, MagicMock
from agents.threat_hunter_agent.main import ThreatHunterAgent


class TestThreatHunterAgent:
    @pytest.fixture
    def agent(self):
        with patch.object(ThreatHunterAgent, '_load_blacklist', return_value={"0xblacklisted"}):
            with patch.object(ThreatHunterAgent, '_load_mixers', return_value={"0xmixer1", "0xmixer2"}):
                return ThreatHunterAgent()

    def test_health(self, agent):
        result = agent.health()
        assert result["status"] == "ok"
        assert result["agent"] == "ThreatHunterAgent"

    def test_blacklisted_address(self, agent):
        result = agent.analyze({"address": "0xblacklisted", "transactions": []})
        assert result["risk_level"] == "critical"
        assert result["total_threats"] >= 1
        assert any(t["type"] == "blacklisted_address" for t in result["threats_detected"])

    def test_mixer_interaction(self, agent):
        transactions = [
            {"from": "0xuser", "to": "0xmixer1", "timestamp": 100},
            {"from": "0xmixer2", "to": "0xuser", "timestamp": 200}
        ]
        result = agent.analyze({"address": "0xuser", "transactions": transactions})
        assert result["total_threats"] >= 1
        threat = next(t for t in result["threats_detected"] if t["type"] == "mixer_interaction")
        assert threat["count"] == 2

    def test_rapid_transactions(self, agent):
        transactions = [{"timestamp": i * 10, "from": "0xuser", "to": "0xother"} for i in range(15)]
        result = agent.analyze({"address": "0xuser", "transactions": transactions})
        assert any(t["type"] == "rapid_transactions" for t in result["threats_detected"])

    def test_no_rapid_transactions_sparse(self, agent):
        transactions = [{"timestamp": i * 1000, "from": "0xuser", "to": "0xother"} for i in range(5)]
        result = agent.analyze({"address": "0xuser", "transactions": transactions})
        assert not any(t["type"] == "rapid_transactions" for t in result["threats_detected"])

    def test_clean_address(self, agent):
        result = agent.analyze({"address": "0xclean", "transactions": []})
        assert result["risk_level"] == "low"
        assert result["total_threats"] == 0

    @patch('requests.post')
    def test_threat_intelligence_integration(self, mock_post, agent):
        agent.threat_intel_api_key = "test_key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"is_threat": True, "severity": "high", "details": "Known scammer"}
        mock_post.return_value = mock_response
        
        result = agent.analyze({"address": "0xscammer", "transactions": []})
        assert any(t["type"] == "external_threat_intel" for t in result["threats_detected"])

    def test_risk_level_calculation(self, agent):
        assert agent._calculate_risk_level(90) == "critical"
        assert agent._calculate_risk_level(60) == "high"
        assert agent._calculate_risk_level(30) == "medium"
        assert agent._calculate_risk_level(10) == "low"

    def test_case_insensitive_addresses(self, agent):
        result = agent.analyze({"address": "0xBLACKLISTED", "transactions": []})
        assert result["risk_level"] == "critical"

    def test_multiple_threats(self, agent):
        transactions = [
            {"from": "0xblacklisted", "to": "0xmixer1", "timestamp": i * 10}
            for i in range(12)
        ]
        result = agent.analyze({"address": "0xblacklisted", "transactions": transactions})
        assert result["total_threats"] >= 2
        assert result["risk_level"] in ["critical", "high"]
