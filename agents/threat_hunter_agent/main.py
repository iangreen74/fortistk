import os
import requests
from typing import Dict, List, Set
from agents.base_agent.base import BaseAgent


class ThreatHunterAgent(BaseAgent):
    """Agent for detecting suspicious patterns and threat intelligence."""

    def __init__(self):
        self.blacklisted_addresses: Set[str] = self._load_blacklist()
        self.mixer_addresses: Set[str] = self._load_mixers()
        self.rapid_tx_threshold = int(os.getenv("RAPID_TX_THRESHOLD", "10"))
        self.rapid_tx_window = int(os.getenv("RAPID_TX_WINDOW_SECONDS", "300"))
        self.threat_intel_api_key = os.getenv("THREAT_INTEL_API_KEY", "")
        self.threat_intel_url = os.getenv(
            "THREAT_INTEL_URL", "https://api.threatintel.example.com/v1/check"
        )

    def _load_blacklist(self) -> Set[str]:
        """Load blacklisted addresses from file or env."""
        blacklist_file = os.getenv("BLACKLIST_FILE", "blacklist.txt")
        if os.path.exists(blacklist_file):
            with open(blacklist_file, "r") as f:
                return set(line.strip().lower() for line in f if line.strip())
        return set(os.getenv("BLACKLISTED_ADDRESSES", "").split(",") if os.getenv("BLACKLISTED_ADDRESSES") else [])

    def _load_mixers(self) -> Set[str]:
        """Load known mixer addresses."""
        mixer_file = os.getenv("MIXER_FILE", "mixers.txt")
        if os.path.exists(mixer_file):
            with open(mixer_file, "r") as f:
                return set(line.strip().lower() for line in f if line.strip())
        return set(os.getenv("MIXER_ADDRESSES", "").split(",") if os.getenv("MIXER_ADDRESSES") else [])

    def analyze(self, input_data: Dict) -> Dict:
        """
        Analyze wallet/transaction for threats.
        
        Args:
            input_data: Dict with 'address', 'transactions' (optional)
        
        Returns:
            Dict with threat assessment
        """
        address = input_data.get("address", "").lower()
        transactions = input_data.get("transactions", [])
        
        threats = []
        risk_score = 0
        
        # Check blacklist
        if self._check_blacklist(address):
            threats.append({"type": "blacklisted_address", "severity": "critical"})
            risk_score += 100
        
        # Check mixer interaction
        mixer_count = self._check_mixer_interaction(address, transactions)
        if mixer_count > 0:
            threats.append({
                "type": "mixer_interaction",
                "severity": "high",
                "count": mixer_count
            })
            risk_score += 50 * mixer_count
        
        # Check rapid transactions
        rapid_tx = self._check_rapid_transactions(transactions)
        if rapid_tx["is_rapid"]:
            threats.append({
                "type": "rapid_transactions",
                "severity": "medium",
                "count": rapid_tx["count"],
                "window_seconds": rapid_tx["window"]
            })
            risk_score += 30
        
        # Check external threat intelligence
        threat_intel = self._query_threat_intelligence(address)
        if threat_intel.get("is_threat"):
            threats.append({
                "type": "external_threat_intel",
                "severity": threat_intel.get("severity", "medium"),
                "details": threat_intel.get("details", "")
            })
            risk_score += 40
        
        return {
            "address": address,
            "risk_score": min(risk_score, 100),
            "risk_level": self._calculate_risk_level(risk_score),
            "threats_detected": threats,
            "total_threats": len(threats)
        }

    def _check_blacklist(self, address: str) -> bool:
        """Check if address is blacklisted."""
        return address in self.blacklisted_addresses

    def _check_mixer_interaction(self, address: str, transactions: List[Dict]) -> int:
        """Check for interactions with known mixers."""
        count = 0
        for tx in transactions:
            to_addr = tx.get("to", "").lower()
            from_addr = tx.get("from", "").lower()
            if to_addr in self.mixer_addresses or from_addr in self.mixer_addresses:
                count += 1
        return count

    def _check_rapid_transactions(self, transactions: List[Dict]) -> Dict:
        """Detect rapid transaction patterns."""
        if len(transactions) < self.rapid_tx_threshold:
            return {"is_rapid": False, "count": 0, "window": 0}
        
        # Sort by timestamp
        sorted_txs = sorted(transactions, key=lambda x: x.get("timestamp", 0))
        
        for i in range(len(sorted_txs) - self.rapid_tx_threshold + 1):
            window_start = sorted_txs[i].get("timestamp", 0)
            window_end = sorted_txs[i + self.rapid_tx_threshold - 1].get("timestamp", 0)
            
            if window_end - window_start <= self.rapid_tx_window:
                return {
                    "is_rapid": True,
                    "count": self.rapid_tx_threshold,
                    "window": window_end - window_start
                }
        
        return {"is_rapid": False, "count": 0, "window": 0}

    def _query_threat_intelligence(self, address: str) -> Dict:
        """Query external threat intelligence API."""
        if not self.threat_intel_api_key:
            return {"is_threat": False}
        
        try:
            response = requests.post(
                self.threat_intel_url,
                json={"address": address},
                headers={"Authorization": f"Bearer {self.threat_intel_api_key}"},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        
        return {"is_threat": False}

    def _calculate_risk_level(self, risk_score: int) -> str:
        """Calculate risk level from score."""
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 50:
            return "high"
        elif risk_score >= 20:
            return "medium"
        else:
            return "low"
