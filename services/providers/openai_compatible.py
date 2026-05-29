import requests
import json
from typing import Dict, Optional
from services.providers.base import BaseProvider


class OpenAICompatibleProvider(BaseProvider):
    """
    通用OpenAI兼容API提供商
    支持所有兼容OpenAI API格式的服务：
    - OpenAI
    - Azure OpenAI
    - Claude (通过代理)
    - 本地模型 (Ollama, vLLM, LMStudio等)
    - DeepSeek
    - Moonshot
    - 智谱AI
    - 百度文心
    - 讯飞星火
    - 等等...
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = 'https://api.openai.com/v1',
        provider_name: str = 'OpenAI Compatible'
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.provider_name = provider_name

    def analyze(self, prompt: str, max_tokens: int = 4096) -> str:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        payload = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': max_tokens,
            'temperature': 0.3
        }

        response = requests.post(
            f'{self.base_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            raise Exception(f'API调用失败: {response.status_code} - {response.text}')

        result = response.json()
        return result['choices'][0]['message']['content']

    def get_model_name(self) -> str:
        return self.model

    def is_available(self) -> bool:
        return bool(self.api_key or 'localhost' in self.base_url or '127.0.0.1' in self.base_url)

    def get_provider_name(self) -> str:
        return self.provider_name
