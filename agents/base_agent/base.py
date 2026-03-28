import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseAgent(ABC):
    """Abstract base class for all agents with lifecycle management."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent with configuration.
        
        Args:
            config: Optional configuration dictionary. If None, loads from environment.
        """
        self.config = config or self._load_config_from_env()
        self.logger = self._setup_logging()
        self._initialized = False
        self._shutdown = False
        self.name = self.__class__.__name__

    def _load_config_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables.
        
        Returns:
            Dictionary containing configuration values.
        """
        return {
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "agent_name": os.getenv("AGENT_NAME", self.__class__.__name__),
            "timeout": int(os.getenv("AGENT_TIMEOUT", "300")),
            "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging with configured level.
        
        Returns:
            Configured logger instance.
        """
        logger = logging.getLogger(self.config.get("agent_name", self.__class__.__name__))
        log_level = self.config.get("log_level", "INFO")
        logger.setLevel(getattr(logging, log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    @abstractmethod
    def initialize(self) -> None:
        """Initialize agent resources and connections.
        
        Raises:
            Exception: If initialization fails.
        """
        pass

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the main agent logic.
        
        Args:
            input_data: Input data for agent processing.
            
        Returns:
            Result dictionary with processing output.
            
        Raises:
            Exception: If execution fails.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup agent resources and connections.
        
        Raises:
            Exception: If shutdown fails.
        """
        pass

    @abstractmethod
    def analyze(self, input_data: Dict) -> Dict:
        """Perform wallet or transaction analysis.
        
        Args:
            input_data: Data to analyze.
            
        Returns:
            Analysis results.
        """
        pass

    def health(self) -> Dict[str, Any]:
        """Check agent health status.
        
        Returns:
            Dictionary containing health status information.
        """
        return {
            "status": "ok" if self._initialized and not self._shutdown else "unavailable",
            "agent": self.name,
            "initialized": self._initialized,
            "shutdown": self._shutdown,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle and log errors consistently.
        
        Args:
            error: The exception that occurred.
            context: Additional context about where the error occurred.
            
        Returns:
            Error information dictionary.
        """
        error_info = {
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "agent": self.name,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logger.error(f"{context}: {error}", exc_info=True)
        return error_info

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False
