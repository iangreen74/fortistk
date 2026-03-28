import os
import pytest
import logging
from unittest.mock import patch
from agents.base_agent.base import BaseAgent


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing."""

    def initialize(self) -> None:
        self._initialized = True
        self.logger.info("Agent initialized")

    def execute(self, input_data: dict) -> dict:
        if not self._initialized:
            raise RuntimeError("Agent not initialized")
        return {"status": "success", "input": input_data}

    def shutdown(self) -> None:
        self._shutdown = True
        self.logger.info("Agent shutdown")

    def analyze(self, input_data: dict) -> dict:
        return {"analysis": "complete", "data": input_data}


class TestBaseAgent:
    """Test suite for BaseAgent class."""

    def test_init_with_config(self):
        """Test initialization with provided config."""
        config = {"log_level": "DEBUG", "agent_name": "TestAgent"}
        agent = ConcreteAgent(config=config)
        assert agent.config == config
        assert agent.name == "ConcreteAgent"
        assert not agent._initialized
        assert not agent._shutdown

    def test_init_without_config(self):
        """Test initialization loading from environment."""
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING", "AGENT_TIMEOUT": "600"}):
            agent = ConcreteAgent()
            assert agent.config["log_level"] == "WARNING"
            assert agent.config["timeout"] == 600

    def test_load_config_from_env(self):
        """Test configuration loading from environment variables."""
        with patch.dict(os.environ, {"LOG_LEVEL": "ERROR", "MAX_RETRIES": "5"}):
            agent = ConcreteAgent()
            config = agent._load_config_from_env()
            assert config["log_level"] == "ERROR"
            assert config["max_retries"] == 5
            assert config["timeout"] == 300  # default

    def test_setup_logging(self):
        """Test logging setup."""
        agent = ConcreteAgent(config={"log_level": "DEBUG", "agent_name": "TestLogger"})
        assert isinstance(agent.logger, logging.Logger)
        assert agent.logger.level == logging.DEBUG

    def test_initialize(self):
        """Test agent initialization."""
        agent = ConcreteAgent()
        agent.initialize()
        assert agent._initialized

    def test_execute(self):
        """Test agent execution."""
        agent = ConcreteAgent()
        agent.initialize()
        result = agent.execute({"test": "data"})
        assert result["status"] == "success"
        assert result["input"]["test"] == "data"

    def test_execute_without_initialize(self):
        """Test execution fails without initialization."""
        agent = ConcreteAgent()
        with pytest.raises(RuntimeError, match="not initialized"):
            agent.execute({"test": "data"})

    def test_shutdown(self):
        """Test agent shutdown."""
        agent = ConcreteAgent()
        agent.shutdown()
        assert agent._shutdown

    def test_analyze(self):
        """Test analyze method."""
        agent = ConcreteAgent()
        result = agent.analyze({"wallet": "0x123"})
        assert result["analysis"] == "complete"
        assert result["data"]["wallet"] == "0x123"

    def test_health_not_initialized(self):
        """Test health check before initialization."""
        agent = ConcreteAgent()
        health = agent.health()
        assert health["status"] == "unavailable"
        assert health["agent"] == "ConcreteAgent"
        assert not health["initialized"]
        assert "timestamp" in health

    def test_health_initialized(self):
        """Test health check after initialization."""
        agent = ConcreteAgent()
        agent.initialize()
        health = agent.health()
        assert health["status"] == "ok"
        assert health["initialized"]

    def test_health_after_shutdown(self):
        """Test health check after shutdown."""
        agent = ConcreteAgent()
        agent.initialize()
        agent.shutdown()
        health = agent.health()
        assert health["status"] == "unavailable"
        assert health["shutdown"]

    def test_handle_error(self):
        """Test error handling."""
        agent = ConcreteAgent()
        error = ValueError("Test error")
        error_info = agent.handle_error(error, "test_context")
        assert error_info["error"] == "Test error"
        assert error_info["error_type"] == "ValueError"
        assert error_info["context"] == "test_context"
        assert error_info["agent"] == "ConcreteAgent"

    def test_context_manager(self):
        """Test context manager protocol."""
        with ConcreteAgent() as agent:
            assert agent._initialized
            result = agent.execute({"test": "data"})
            assert result["status"] == "success"
        assert agent._shutdown
