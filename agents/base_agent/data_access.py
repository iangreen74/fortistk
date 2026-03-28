import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


class DataAccessLayer:
    """Data access layer with caching for agents."""

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "dev")
        self.dynamodb = boto3.resource("dynamodb")
        self.cache = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True,
        )
        self.cache_ttl = int(os.getenv("CACHE_TTL", 300))
        self._init_tables()

    def _init_tables(self):
        """Initialize DynamoDB table references."""
        self.wallet_scores_table = self.dynamodb.Table(f"{self.environment}-wallet-scores")
        self.analysis_history_table = self.dynamodb.Table(f"{self.environment}-analysis-history")
        self.agent_state_table = self.dynamodb.Table(f"{self.environment}-agent-state")

    @contextmanager
    def get_db_connection(self):
        """Get PostgreSQL connection context manager."""
        conn = psycopg2.connect(
            host=os.getenv("RDS_HOST"),
            port=os.getenv("RDS_PORT", 5432),
            database=os.getenv("RDS_DATABASE"),
            user=os.getenv("RDS_USER"),
            password=os.getenv("RDS_PASSWORD"),
        )
        try:
            yield conn
        finally:
            conn.close()

    def get_wallet_score(self, wallet_address: str, use_cache: bool = True) -> Optional[Dict]:
        """Get latest wallet score with caching."""
        cache_key = f"wallet_score:{wallet_address}"
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return json.loads(cached)

        try:
            response = self.wallet_scores_table.query(
                KeyConditionExpression="wallet_address = :addr",
                ExpressionAttributeValues={":addr": wallet_address},
                ScanIndexForward=False,
                Limit=1,
            )
            if response["Items"]:
                score = response["Items"][0]
                self.cache.setex(cache_key, self.cache_ttl, json.dumps(score))
                return score
        except ClientError as e:
            print(f"Error fetching wallet score: {e}")
        return None

    def save_wallet_score(self, wallet_address: str, score_data: Dict) -> bool:
        """Save wallet score to DynamoDB."""
        try:
            timestamp = int(time.time())
            ttl = timestamp + (90 * 24 * 60 * 60)  # 90 days retention
            item = {
                "wallet_address": wallet_address,
                "timestamp": timestamp,
                "ttl": ttl,
                **score_data,
            }
            self.wallet_scores_table.put_item(Item=item)
            self.cache.delete(f"wallet_score:{wallet_address}")
            return True
        except ClientError as e:
            print(f"Error saving wallet score: {e}")
            return False

    def save_analysis_history(self, analysis_id: str, wallet_address: str, analysis_data: Dict) -> bool:
        """Save analysis history."""
        try:
            timestamp = int(time.time())
            ttl = timestamp + (180 * 24 * 60 * 60)  # 180 days retention
            item = {
                "analysis_id": analysis_id,
                "timestamp": timestamp,
                "wallet_address": wallet_address,
                "ttl": ttl,
                **analysis_data,
            }
            self.analysis_history_table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error saving analysis history: {e}")
            return False

    def get_agent_state(self, agent_id: str) -> Optional[Dict]:
        """Get latest agent state."""
        try:
            response = self.agent_state_table.query(
                KeyConditionExpression="agent_id = :id",
                ExpressionAttributeValues={":id": agent_id},
                ScanIndexForward=False,
                Limit=1,
            )
            return response["Items"][0] if response["Items"] else None
        except ClientError as e:
            print(f"Error fetching agent state: {e}")
            return None

    def save_agent_state(self, agent_id: str, state_data: Dict) -> bool:
        """Save agent state."""
        try:
            item = {"agent_id": agent_id, "state_timestamp": int(time.time()), **state_data}
            self.agent_state_table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error saving agent state: {e}")
            return False

    def query_transaction_graph(self, wallet_address: str, depth: int = 2) -> List[Dict]:
        """Query transaction graph from PostgreSQL."""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    WITH RECURSIVE tx_graph AS (
                        SELECT from_address, to_address, amount, timestamp, 1 as depth
                        FROM transactions
                        WHERE from_address = %s OR to_address = %s
                        UNION ALL
                        SELECT t.from_address, t.to_address, t.amount, t.timestamp, tg.depth + 1
                        FROM transactions t
                        JOIN tx_graph tg ON t.from_address = tg.to_address OR t.to_address = tg.from_address
                        WHERE tg.depth < %s
                    )
                    SELECT * FROM tx_graph;
                """
                cursor.execute(query, (wallet_address, wallet_address, depth))
                return cursor.fetchall()

    def invalidate_cache(self, pattern: str):
        """Invalidate cache entries matching pattern."""
        for key in self.cache.scan_iter(match=pattern):
            self.cache.delete(key)