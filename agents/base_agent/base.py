from abc import ABC, abstractmethod
from typing import Dict

class BaseAgent(ABC):
    @abstractmethod
    def analyze(self, input_data: Dict) -> Dict:
        """Perform wallet or transaction analysis."""
        pass

    def health(self) -> Dict:
        return {
            "status": "ok",
            "agent": self.__class__.__name__
        }
