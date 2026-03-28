#!/usr/bin/env python3
"""CLI tool for managing blockchain analysis agents.

Provides commands for:
- Starting/stopping agents
- Viewing logs
- Health checks
- Configuration updates
- Status monitoring

Examples:
    python cli/manage_agents.py start wallet_score_agent
    python cli/manage_agents.py status --all
    python cli/manage_agents.py logs threat_hunter_agent --tail 50
    python cli/manage_agents.py health --agent tx_analyzer_agent
    python cli/manage_agents.py config wallet_score_agent --set key=value
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


AGENTS_DIR = Path(__file__).parent.parent / "agents"
LOGS_DIR = Path(__file__).parent.parent / "logs"
CONFIG_DIR = Path(__file__).parent.parent / "config"


class AgentManager:
    """Manager for blockchain analysis agents."""

    def __init__(self):
        self.agents_dir = AGENTS_DIR
        self.logs_dir = LOGS_DIR
        self.config_dir = CONFIG_DIR
        self.logs_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)

    def list_agents(self) -> List[str]:
        """List all available agents."""
        if not self.agents_dir.exists():
            return []
        return [d.name for d in self.agents_dir.iterdir() 
                if d.is_dir() and not d.name.startswith(".") and d.name != "base_agent"]

    def start_agent(self, agent_name: str, port: Optional[int] = None) -> bool:
        """Start an agent container."""
        if agent_name not in self.list_agents():
            print(f"Error: Agent '{agent_name}' not found")
            return False

        try:
            cmd = ["docker", "run", "-d", "--name", agent_name]
            if port:
                cmd.extend(["-p", f"{port}:{port}"])
            cmd.append(f"{agent_name}:latest")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Started agent: {agent_name}")
                return True
            else:
                print(f"Error starting agent: {result.stderr}")
                return False
        except Exception as e:
            print(f"Exception starting agent: {e}")
            return False

    def stop_agent(self, agent_name: str) -> bool:
        """Stop a running agent container."""
        try:
            result = subprocess.run(
                ["docker", "stop", agent_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                subprocess.run(["docker", "rm", agent_name], capture_output=True)
                print(f"Stopped agent: {agent_name}")
                return True
            else:
                print(f"Error stopping agent: {result.stderr}")
                return False
        except Exception as e:
            print(f"Exception stopping agent: {e}")
            return False

    def status(self, agent_name: Optional[str] = None) -> Dict:
        """Get status of agents."""
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{json .}}"],
                capture_output=True,
                text=True
            )
            statuses = {}
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                container = json.loads(line)
                name = container.get("Names", "")
                if name in self.list_agents():
                    if agent_name is None or name == agent_name:
                        statuses[name] = {
                            "status": container.get("Status", "unknown"),
                            "state": container.get("State", "unknown")
                        }
            return statuses
        except Exception as e:
            print(f"Error getting status: {e}")
            return {}

    def logs(self, agent_name: str, tail: int = 100) -> None:
        """View agent logs."""
        try:
            subprocess.run(
                ["docker", "logs", "--tail", str(tail), agent_name],
                check=True
            )
        except subprocess.CalledProcessError:
            print(f"Error: Could not retrieve logs for {agent_name}")

    def health_check(self, agent_name: str) -> Dict:
        """Perform health check on agent."""
        import requests
        try:
            response = requests.get(f"http://localhost:8000/health", timeout=5)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Manage blockchain analysis agents")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start an agent")
    start_parser.add_argument("agent", help="Agent name")
    start_parser.add_argument("--port", type=int, help="Port to expose")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop an agent")
    stop_parser.add_argument("agent", help="Agent name")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get agent status")
    status_parser.add_argument("--agent", help="Specific agent name")
    status_parser.add_argument("--all", action="store_true", help="All agents")

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View agent logs")
    logs_parser.add_argument("agent", help="Agent name")
    logs_parser.add_argument("--tail", type=int, default=100, help="Number of lines")

    # Health command
    health_parser = subparsers.add_parser("health", help="Health check")
    health_parser.add_argument("--agent", help="Agent name")

    # List command
    subparsers.add_parser("list", help="List all agents")

    args = parser.parse_args()
    manager = AgentManager()

    if args.command == "start":
        manager.start_agent(args.agent, args.port)
    elif args.command == "stop":
        manager.stop_agent(args.agent)
    elif args.command == "status":
        statuses = manager.status(args.agent if not args.all else None)
        print(json.dumps(statuses, indent=2))
    elif args.command == "logs":
        manager.logs(args.agent, args.tail)
    elif args.command == "health":
        if args.agent:
            health = manager.health_check(args.agent)
            print(json.dumps(health, indent=2))
    elif args.command == "list":
        agents = manager.list_agents()
        for agent in agents:
            print(agent)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
