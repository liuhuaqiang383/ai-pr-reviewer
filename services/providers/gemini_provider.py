import google.generativeai as genai
from typing import Optional
from services.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Google Gemini API provider"""

    AVAILABLE_MODELS = {
        'gemini-1.5-pro': 'Gemini 1.5 Pro (推荐)',
        'gemini-1.5-flash': 'Gemini 1.5 Flash (快速)',
        'gemini-1.0-pro': 'Gemini 1.0 Pro',
    }

    def __init__(self, api_key: str, model: str = 'gemini-1.5-pro'):
        self.api_key = api_key
        self.model = model
        if api_key:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
        else:
            self.client = None

    def analyze(self, prompt: str, max_tokens: int = 4096) -> str:
        if not self.client:
            raise ValueError("Gemini API key not configured")

        response = self.client.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens
            )
        )
        return response.text

    def get_model_name(self) -> str:
        return self.model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def get_provider_name(self) -> str:
        return 'Gemini'

    @staticmethod
    def get_models():
        return GeminiProvider.AVAILABLE_MODELS
