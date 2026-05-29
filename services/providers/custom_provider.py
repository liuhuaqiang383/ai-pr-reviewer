import requests
import json
from typing import Dict, Optional, Any
from services.providers.base import BaseProvider


class CustomProvider(BaseProvider):
    """
    完全自定义的API提供商
    支持任意API格式，通过配置模板定义请求和响应格式
    """

    def __init__(
        self,
        config: Dict[str, Any]
    ):
        """
        config示例:
        {
            "name": "My Custom LLM",
            "base_url": "http://localhost:8080/v1",
            "api_key": "optional-key",
            "headers": {"X-Custom": "value"},
            "request_format": {
                "method": "POST",
                "path": "/chat/completions",
                "body_template": {
                    "model": "{model}",
                    "messages": "{messages}",
                    "max_tokens": "{max_tokens}",
                    "temperature": 0.3
                }
            },
            "response_format": {
                "content_path": "choices.0.message.content"
            },
            "model": "my-model"
        }
        """
        self.config = config
        self.name = config.get('name', 'Custom Provider')
        self.base_url = config.get('base_url', '').rstrip('/')
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', 'default')
        self.extra_headers = config.get('headers', {})
        self.request_format = config.get('request_format', {})
        self.response_format = config.get('response_format', {})

    def analyze(self, prompt: str, max_tokens: int = 4096) -> str:
        # Build headers
        headers = {
            'Content-Type': 'application/json',
            **self.extra_headers
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        # Build request body from template
        body_template = self.request_format.get('body_template', {})
        messages = [{'role': 'user', 'content': prompt}]

        body = self._fill_template(body_template, {
            'model': self.model,
            'messages': messages,
            'max_tokens': max_tokens,
            'prompt': prompt
        })

        # Get path
        path = self.request_format.get('path', '/chat/completions')

        # Make request
        response = requests.post(
            f'{self.base_url}{path}',
            headers=headers,
            json=body,
            timeout=180
        )

        if response.status_code != 200:
            raise Exception(f'API调用失败: {response.status_code} - {response.text}')

        # Parse response
        result = response.json()
        return self._extract_content(result)

    def _fill_template(self, template: Any, variables: Dict) -> Any:
        """Fill template with variables"""
        if isinstance(template, str):
            for key, value in variables.items():
                template = template.replace(f'{{{key}}}', str(value))
            return template
        elif isinstance(template, dict):
            return {k: self._fill_template(v, variables) for k, v in template.items()}
        elif isinstance(template, list):
            return [self._fill_template(item, variables) for item in template]
        return template

    def _extract_content(self, response: Dict) -> str:
        """Extract content from response using configured path"""
        content_path = self.response_format.get('content_path', 'choices.0.message.content')

        # Support dot notation for nested access
        parts = content_path.split('.')
        result = response
        for part in parts:
            if isinstance(result, list):
                result = result[int(part)]
            elif isinstance(result, dict):
                result = result.get(part, '')
            else:
                break

        return str(result) if result else ''

    def get_model_name(self) -> str:
        return self.model

    def is_available(self) -> bool:
        return bool(self.base_url)

    def get_provider_name(self) -> str:
        return self.name
