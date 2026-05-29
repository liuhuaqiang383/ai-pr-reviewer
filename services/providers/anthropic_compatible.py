import requests
import json
from typing import Dict, Optional
from services.providers.base import BaseProvider


class AnthropicCompatibleProvider(BaseProvider):
    """
    通用Anthropic兼容API提供商
    支持Claude API格式的服务：
    - Anthropic官方API
    - Claude代理服务
    - AWS Bedrock Claude
    - Google Vertex AI Claude
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = 'https://api.anthropic.com/v1',
        provider_name: str = 'Anthropic Compatible'
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.provider_name = provider_name

    def analyze(self, prompt: str, max_tokens: int = 4096) -> str:
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }

        payload = {
            'model': self.model,
            'max_tokens': max_tokens,
            'messages': [{'role': 'user', 'content': prompt}]
        }

        response = requests.post(
            f'{self.base_url}/messages',
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            raise Exception(f'API调用失败: {response.status_code} - {response.text}')

        result = response.json()
        return result['content'][0]['text']

    def get_model_name(self) -> str:
        return self.model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def get_provider_name(self) -> str:
        return self.provider_name
