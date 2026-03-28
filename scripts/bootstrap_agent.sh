#!/bin/bash
# Bootstrap script for creating new blockchain analysis agents
# Usage: ./scripts/bootstrap_agent.sh <agent_name>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <agent_name>"
    echo "Example: $0 wallet_score_agent"
    exit 1
fi

AGENT_NAME="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT_DIR="${ROOT_DIR}/agents/${AGENT_NAME}"

echo "==> Bootstrapping new agent: ${AGENT_NAME}"

if [ -d "${AGENT_DIR}" ]; then
    echo "Error: Agent directory already exists: ${AGENT_DIR}"
    exit 1
fi

# Create agent directory structure
echo "==> Creating directory structure..."
mkdir -p "${AGENT_DIR}"
mkdir -p "${AGENT_DIR}/tests"
mkdir -p "${AGENT_DIR}/config"

# Create main agent file
echo "==> Creating agent implementation..."
cat > "${AGENT_DIR}/agent.py" << 'EOF'
from agents.base_agent.base import BaseAgent
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class Agent(BaseAgent):
    """Agent for blockchain analysis."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def analyze(self, input_data: Dict) -> Dict:
        """Perform analysis on input data."""
        logger.info(f"Analyzing: {input_data}")
        # TODO: Implement analysis logic
        return {
            "status": "success",
            "result": {}
        }
EOF

# Create Dockerfile
echo "==> Creating Dockerfile..."
cat > "${AGENT_DIR}/Dockerfile" << EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "agent.py"]
EOF

# Create requirements.txt
echo "==> Creating requirements.txt..."
cat > "${AGENT_DIR}/requirements.txt" << EOF
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
EOF

# Create README
echo "==> Creating README.md..."
cat > "${AGENT_DIR}/README.md" << EOF
# ${AGENT_NAME}

## Overview

Blockchain analysis agent for [describe purpose].

## Features

- Feature 1
- Feature 2
- Feature 3

## Usage

\`\`\`bash
# Build the agent
docker build -t ${AGENT_NAME} .

# Run the agent
docker run -p 8000:8000 ${AGENT_NAME}

# Using CLI
python cli/manage_agents.py start ${AGENT_NAME}
\`\`\`

## Configuration

Configuration options:
- \`key1\`: Description
- \`key2\`: Description

## Development

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Run locally
python agent.py
\`\`\`

## API Endpoints

- \`POST /analyze\`: Perform analysis
- \`GET /health\`: Health check

## Examples

\`\`\`python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"data": "example"}
)
print(response.json())
\`\`\`
EOF

# Create test file
echo "==> Creating test file..."
cat > "${AGENT_DIR}/tests/test_agent.py" << 'EOF'
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import Agent

def test_agent_initialization():
    agent = Agent()
    assert agent is not None

def test_analyze():
    agent = Agent()
    result = agent.analyze({"test": "data"})
    assert result["status"] == "success"

def test_health():
    agent = Agent()
    health = agent.health()
    assert health["status"] == "ok"
EOF

# Create config file
echo "==> Creating config file..."
cat > "${AGENT_DIR}/config/config.yaml" << EOF
agent:
  name: ${AGENT_NAME}
  version: 0.1.0
  
settings:
  log_level: INFO
  timeout: 30
EOF

echo ""
echo "==> Agent '${AGENT_NAME}' created successfully!"
echo ""
echo "Next steps:"
echo "  1. cd ${AGENT_DIR}"
echo "  2. Implement analysis logic in agent.py"
echo "  3. docker build -t ${AGENT_NAME} ."
echo "  4. python ../cli/manage_agents.py start ${AGENT_NAME}"
echo ""
