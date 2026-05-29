from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseProvider(ABC):
    """Base class for AI providers"""

    @abstractmethod
    def analyze(self, prompt: str, max_tokens: int = 4096) -> str:
        """Send prompt to AI and get response"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get current model name"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available"""
        pass

    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.__class__.__name__
