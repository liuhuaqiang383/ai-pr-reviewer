from typing import Dict, Optional, List
from services.providers.base import BaseProvider
from services.providers.claude_provider import ClaudeProvider
from services.providers.openai_provider import OpenAIProvider
from services.providers.gemini_provider import GeminiProvider
from config import Config


class ProviderFactory:
    """Factory for creating AI providers"""

    PROVIDERS = {
        'claude': ClaudeProvider,
        'openai': OpenAIProvider,
        'gemini': GeminiProvider,
    }

    @classmethod
    def create_provider(cls, provider_name: Optional[str] = None, model: Optional[str] = None) -> BaseProvider:
        """Create an AI provider instance"""
        # Use configured provider or default to claude
        provider_name = provider_name or Config.AI_PROVIDER

        if provider_name not in cls.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(cls.PROVIDERS.keys())}")

        # Get API key and model from config
        api_key = cls._get_api_key(provider_name)
        model = model or cls._get_default_model(provider_name)

        # Create provider instance
        provider_class = cls.PROVIDERS[provider_name]
        return provider_class(api_key=api_key, model=model)

    @classmethod
    def _get_api_key(cls, provider_name: str) -> str:
        """Get API key for provider"""
        key_map = {
            'claude': Config.CLAUDE_API_KEY,
            'openai': Config.OPENAI_API_KEY,
            'gemini': Config.GEMINI_API_KEY,
        }
        return key_map.get(provider_name, '')

    @classmethod
    def _get_default_model(cls, provider_name: str) -> str:
        """Get default model for provider"""
        model_map = {
            'claude': Config.CLAUDE_MODEL,
            'openai': Config.OPENAI_MODEL,
            'gemini': Config.GEMINI_MODEL,
        }
        return model_map.get(provider_name, '')

    @classmethod
    def get_available_providers(cls) -> Dict[str, Dict]:
        """Get list of available providers and their status"""
        result = {}
        for name, provider_class in cls.PROVIDERS.items():
            api_key = cls._get_api_key(name)
            result[name] = {
                'name': name,
                'available': bool(api_key),
                'models': provider_class.get_models(),
                'current_model': cls._get_default_model(name),
            }
        return result

    @classmethod
    def get_all_models(cls) -> Dict[str, List[str]]:
        """Get all available models grouped by provider"""
        models = {}
        for name, provider_class in cls.PROVIDERS.items():
            if cls._get_api_key(name):
                models[name] = list(provider_class.get_models().keys())
        return models
