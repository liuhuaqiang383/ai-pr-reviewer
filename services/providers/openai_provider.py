import openai
from typing import Optional
from services.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI GPT API provider"""

    AVAILABLE_MODELS = {
        'gpt-4o': 'GPT-4o (推荐)',
        'gpt-4o-mini': 'GPT-4o Mini (快速)',
        'gpt-4-turbo': 'GPT-4 Turbo',
        'gpt-3.5-turbo': 'GPT-3.5 Turbo (经济)',
    }

    def __init__(self, api_key: str, model: str = 'gpt-4o'):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=api_key) if api_key else None

    def analyze(self, prompt: str, max_tokens: int = 4096) -> str:
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def get_model_name(self) -> str:
        return self.model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def get_provider_name(self) -> str:
        return 'OpenAI'

    @staticmethod
    def get_models():
        return OpenAIProvider.AVAILABLE_MODELS
