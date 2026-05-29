import anthropic
from typing import Optional
from services.providers.base import BaseProvider


class ClaudeProvider(BaseProvider):
    """Claude API provider"""

    AVAILABLE_MODELS = {
        'claude-haiku-4-20250514': 'Claude Haiku (快速)',
        'claude-sonnet-4-20250514': 'Claude Sonnet (平衡)',
        'claude-opus-4-20250514': 'Claude Opus (高质量)',
    }

    def __init__(self, api_key: str, model: str = 'claude-sonnet-4-20250514'):
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None

    def analyze(self, prompt: str, max_tokens: int = 4096) -> str:
        if not self.client:
            raise ValueError("Claude API key not configured")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def get_model_name(self) -> str:
        return self.model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def get_provider_name(self) -> str:
        return 'Claude'

    @staticmethod
    def get_models():
        return ClaudeProvider.AVAILABLE_MODELS
