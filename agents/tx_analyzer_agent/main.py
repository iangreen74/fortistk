from typing import Dict, List, Optional
import os
import logging
from collections import defaultdict
from datetime import datetime, timedelta
import statistics

try:
    from agents.base_agent.base import BaseAgent
except ImportError:
    from base_agent.base import BaseAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransactionAnalyzerAgent(BaseAgent):
    """Agent for analyzing transaction flows, entity clustering, and anomaly detection."""

    def __init__(self):
        self.volume_threshold = float(os.getenv("VOLUME_THRESHOLD", "10000"))
        self.velocity_threshold = int(os.getenv("VELOCITY_THRESHOLD", "50"))
        self.time_window_hours = int(os.getenv("TIME_WINDOW_HOURS", "24"))

    def analyze(self, input_data: Dict) -> Dict:
        """Analyze transaction patterns and detect anomalies."""
        wallet_address = input_data.get("wallet_address")
        transactions = input_data.get("transactions", [])

        if not wallet_address:
            return {"error": "wallet_address is required"}

        # Perform analyses
        flow_analysis = self._analyze_transaction_flow(transactions, wallet_address)
        entity_clusters = self._detect_entity_clusters(transactions, wallet_address)
        anomalies = self._detect_anomalies(transactions)
        risk_score = self._calculate_risk_score(flow_analysis, entity_clusters, anomalies)

        return {
            "wallet_address": wallet_address,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "transaction_count": len(transactions),
            "flow_analysis": flow_analysis,
            "entity_clusters": entity_clusters,
            "anomalies": anomalies,
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score)
        }

    def _analyze_transaction_flow(self, transactions: List[Dict], wallet: str) -> Dict:
        """Analyze transaction flow patterns."""
        inflow = {"count": 0, "total_value": 0, "addresses": set()}
        outflow = {"count": 0, "total_value": 0, "addresses": set()}

        for tx in transactions:
            from_addr = tx.get("from")
            to_addr = tx.get("to")
            value = float(tx.get("value", 0))

            if to_addr == wallet:
                inflow["count"] += 1
                inflow["total_value"] += value
                inflow["addresses"].add(from_addr)
            elif from_addr == wallet:
                outflow["count"] += 1
                outflow["total_value"] += value
                outflow["addresses"].add(to_addr)

        return {
            "inflow": {
                "count": inflow["count"],
                "total_value": inflow["total_value"],
                "unique_sources": len(inflow["addresses"])
            },
            "outflow": {
                "count": outflow["count"],
                "total_value": outflow["total_value"],
                "unique_destinations": len(outflow["addresses"])
            },
            "net_flow": inflow["total_value"] - outflow["total_value"]
        }

    def _detect_entity_clusters(self, transactions: List[Dict], wallet: str) -> Dict:
        """Detect potential entity clusters based on transaction patterns."""
        interaction_count = defaultdict(int)
        interaction_value = defaultdict(float)

        for tx in transactions:
            from_addr = tx.get("from")
            to_addr = tx.get("to")
            value = float(tx.get("value", 0))

            counterparty = to_addr if from_addr == wallet else from_addr
            if counterparty and counterparty != wallet:
                interaction_count[counterparty] += 1
                interaction_value[counterparty] += value

        # Identify high-frequency counterparties
        clusters = []
        for addr, count in interaction_count.items():
            if count >= 5:  # Threshold for clustering
                clusters.append({
                    "address": addr,
                    "interaction_count": count,
                    "total_value": interaction_value[addr],
                    "cluster_type": "high_frequency"
                })

        return {
            "cluster_count": len(clusters),
            "clusters": clusters[:10]  # Top 10 clusters
        }

    def _detect_anomalies(self, transactions: List[Dict]) -> Dict:
        """Detect volume and velocity anomalies."""
        anomalies = {"volume": [], "velocity": [], "detected": False}

        if not transactions:
            return anomalies

        # Volume anomaly detection
        values = [float(tx.get("value", 0)) for tx in transactions]
        if values:
            avg_value = statistics.mean(values)
            for tx in transactions:
                value = float(tx.get("value", 0))
                if value > self.volume_threshold or value > avg_value * 10:
                    anomalies["volume"].append({
                        "tx_hash": tx.get("hash"),
                        "value": value,
                        "reason": "unusually_high_value"
                    })

        # Velocity anomaly detection (transactions per time window)
        sorted_txs = sorted(transactions, key=lambda x: x.get("timestamp", 0))
        time_window = timedelta(hours=self.time_window_hours)

        for i, tx in enumerate(sorted_txs):
            tx_time = datetime.fromtimestamp(tx.get("timestamp", 0))
            window_start = tx_time - time_window
            recent_txs = [t for t in sorted_txs[:i+1] if datetime.fromtimestamp(t.get("timestamp", 0)) >= window_start]

            if len(recent_txs) > self.velocity_threshold:
                anomalies["velocity"].append({
                    "timestamp": tx_time.isoformat(),
                    "tx_count_in_window": len(recent_txs),
                    "reason": "high_transaction_velocity"
                })
                break

        anomalies["detected"] = bool(anomalies["volume"] or anomalies["velocity"])
        return anomalies

    def _calculate_risk_score(self, flow: Dict, clusters: Dict, anomalies: Dict) -> float:
        """Calculate risk score based on multiple factors."""
        score = 0.0

        # Flow-based risk (0-30 points)
        net_flow = abs(flow.get("net_flow", 0))
        if net_flow > 100000:
            score += 30
        elif net_flow > 50000:
            score += 20
        elif net_flow > 10000:
            score += 10

        # Clustering risk (0-30 points)
        cluster_count = clusters.get("cluster_count", 0)
        if cluster_count > 10:
            score += 30
        elif cluster_count > 5:
            score += 20
        elif cluster_count > 2:
            score += 10

        # Anomaly risk (0-40 points)
        if anomalies.get("detected"):
            score += len(anomalies.get("volume", [])) * 10
            score += len(anomalies.get("velocity", [])) * 15

        return min(score, 100.0)

    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to categorical level."""
        if score >= 70:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"
