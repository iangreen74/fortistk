from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

class BaseAgent:
    def analyze(self, input_data: dict) -> dict:
        raise NotImplementedError
    def health(self) -> dict:
        return {"status": "ok", "agent": "wallet_score_agent"}

class WalletInput(BaseModel):
    address: str

class WalletScoreAgent(BaseAgent):
    def analyze(self, input_data: Dict) -> Dict:
        score = 42  # Dummy logic
        return {
            "wallet": input_data["address"],
            "risk_score": score,
            "verdict": "moderate"
        }

agent = WalletScoreAgent()

@app.get("/health")
def health():
    return agent.health()

@app.post("/analyze")
def analyze_wallet(data: WalletInput):
    return agent.analyze(data.dict())
