import json
from typing import Dict, Optional, List, Any
from services.providers.base import BaseProvider
from services.providers.openai_compatible import OpenAICompatibleProvider
from services.providers.anthropic_compatible import AnthropicCompatibleProvider
from services.providers.custom_provider import CustomProvider
from config import Config


class ProviderFactory:
    """
    动态AI提供商工厂
    支持通过配置文件或API动态添加任意模型
    """

    # 内置提供商模板
    BUILTIN_TEMPLATES = {
        'openai': {
            'name': 'OpenAI',
            'type': 'openai_compatible',
            'base_url': 'https://api.openai.com/v1',
            'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo']
        },
        'claude': {
            'name': 'Claude',
            'type': 'anthropic_compatible',
            'base_url': 'https://api.anthropic.com/v1',
            'models': ['claude-sonnet-4-20250514', 'claude-opus-4-20250514', 'claude-haiku-4-20250514']
        },
        'gemini': {
            'name': 'Gemini',
            'type': 'openai_compatible',
            'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai',
            'models': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro']
        },
        'deepseek': {
            'name': 'DeepSeek',
            'type': 'openai_compatible',
            'base_url': 'https://api.deepseek.com/v1',
            'models': ['deepseek-chat', 'deepseek-coder']
        },
        'moonshot': {
            'name': 'Moonshot',
            'type': 'openai_compatible',
            'base_url': 'https://api.moonshot.cn/v1',
            'models': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k']
        },
        'zhipu': {
            'name': '智谱AI',
            'type': 'openai_compatible',
            'base_url': 'https://open.bigmodel.cn/api/paas/v4',
            'models': ['glm-4', 'glm-4-flash', 'glm-3-turbo']
        },
        'qwen': {
            'name': '通义千问',
            'type': 'openai_compatible',
            'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'models': ['qwen-turbo', 'qwen-plus', 'qwen-max']
        },
        'ollama': {
            'name': 'Ollama (本地)',
            'type': 'openai_compatible',
            'base_url': 'http://localhost:11434/v1',
            'models': ['llama3', 'codellama', 'mistral', 'qwen2']
        },
        'lmstudio': {
            'name': 'LM Studio (本地)',
            'type': 'openai_compatible',
            'base_url': 'http://localhost:1234/v1',
            'models': ['local-model']
        },
        'vllm': {
            'name': 'vLLM',
            'type': 'openai_compatible',
            'base_url': 'http://localhost:8000/v1',
            'models': ['default']
        }
    }

    def __init__(self):
        self.custom_providers = Config.CUSTOM_PROVIDERS or {}

    def create_provider(
        self,
        provider_id: Optional[str] = None,
        model: Optional[str] = None,
        custom_config: Optional[Dict] = None
    ) -> BaseProvider:
        """
        创建AI提供商实例

        Args:
            provider_id: 提供商标识 (内置或自定义)
            model: 模型名称
            custom_config: 完整的自定义配置
        """
        # 如果提供了完整自定义配置
        if custom_config:
            return self._create_from_config(custom_config)

        # 使用自定义提供商配置
        if provider_id and provider_id in self.custom_providers:
            config = self.custom_providers[provider_id]
            if model:
                config['model'] = model
            return self._create_from_config(config)

        # 使用内置提供商模板
        if provider_id and provider_id in self.BUILTIN_TEMPLATES:
            return self._create_builtin(provider_id, model)

        # 默认使用配置文件中的设置
        return self._create_default()

    def _create_from_config(self, config: Dict) -> BaseProvider:
        """从配置创建提供商"""
        provider_type = config.get('type', 'openai_compatible')

        if provider_type == 'openai_compatible':
            return OpenAICompatibleProvider(
                api_key=config.get('api_key', ''),
                model=config.get('model', 'default'),
                base_url=config.get('base_url', ''),
                provider_name=config.get('name', 'Custom')
            )
        elif provider_type == 'anthropic_compatible':
            return AnthropicCompatibleProvider(
                api_key=config.get('api_key', ''),
                model=config.get('model', 'claude-sonnet-4-20250514'),
                base_url=config.get('base_url', 'https://api.anthropic.com/v1'),
                provider_name=config.get('name', 'Claude')
            )
        elif provider_type == 'custom':
            return CustomProvider(config)
        else:
            raise ValueError(f"未知的提供商类型: {provider_type}")

    def _create_builtin(self, provider_id: str, model: Optional[str] = None) -> BaseProvider:
        """创建内置提供商"""
        template = self.BUILTIN_TEMPLATES[provider_id]
        provider_type = template['type']
        api_key = Config.AI_API_KEYS.get(provider_id, '')

        if provider_type == 'openai_compatible':
            return OpenAICompatibleProvider(
                api_key=api_key,
                model=model or template['models'][0],
                base_url=template['base_url'],
                provider_name=template['name']
            )
        elif provider_type == 'anthropic_compatible':
            return AnthropicCompatibleProvider(
                api_key=api_key,
                model=model or template['models'][0],
                base_url=template['base_url'],
                provider_name=template['name']
            )

    def _create_default(self) -> BaseProvider:
        """创建默认提供商"""
        default_id = Config.DEFAULT_AI_PROVIDER
        default_model = Config.DEFAULT_AI_MODEL
        return self.create_provider(default_id, default_model)

    def get_available_providers(self) -> Dict[str, Dict]:
        """获取所有可用提供商"""
        result = {}

        # 内置提供商
        for pid, template in self.BUILTIN_TEMPLATES.items():
            api_key = Config.AI_API_KEYS.get(pid, '')
            result[pid] = {
                'id': pid,
                'name': template['name'],
                'type': template['type'],
                'base_url': template['base_url'],
                'models': template['models'],
                'available': bool(api_key) or 'localhost' in template['base_url'] or '127.0.0.1' in template['base_url'],
                'is_custom': False
            }

        # 自定义提供商
        for pid, config in self.custom_providers.items():
            result[pid] = {
                'id': pid,
                'name': config.get('name', pid),
                'type': config.get('type', 'custom'),
                'base_url': config.get('base_url', ''),
                'models': config.get('models', [config.get('model', 'default')]),
                'available': bool(config.get('api_key')) or 'localhost' in config.get('base_url', ''),
                'is_custom': True
            }

        return result

    def get_all_models(self) -> Dict[str, List[str]]:
        """获取所有可用模型"""
        providers = self.get_available_providers()
        return {
            pid: info['models']
            for pid, info in providers.items()
            if info['available']
        }
