import os
import json
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration - 支持任意AI模型"""

    # GitHub Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_API_BASE = 'https://api.github.com'

    # Default AI Provider
    DEFAULT_AI_PROVIDER = os.getenv('DEFAULT_AI_PROVIDER', 'openai')
    DEFAULT_AI_MODEL = os.getenv('DEFAULT_AI_MODEL', 'gpt-4o')

    # API Keys for built-in providers
    AI_API_KEYS = {
        'openai': os.getenv('OPENAI_API_KEY', ''),
        'claude': os.getenv('CLAUDE_API_KEY', ''),
        'gemini': os.getenv('GEMINI_API_KEY', ''),
        'deepseek': os.getenv('DEEPSEEK_API_KEY', ''),
        'moonshot': os.getenv('MOONSHOT_API_KEY', ''),
        'zhipu': os.getenv('ZHIPU_API_KEY', ''),
        'qwen': os.getenv('QWEN_API_KEY', ''),
        'ollama': os.getenv('OLLAMA_API_KEY', ''),  # 本地模型通常不需要key
        'lmstudio': os.getenv('LMSTUDIO_API_KEY', ''),
        'vllm': os.getenv('VLLM_API_KEY', ''),
    }

    # Custom providers configuration (JSON string or file path)
    CUSTOM_PROVIDERS_JSON = os.getenv('CUSTOM_PROVIDERS', '{}')
    try:
        CUSTOM_PROVIDERS = json.loads(CUSTOM_PROVIDERS_JSON) if CUSTOM_PROVIDERS_JSON else {}
    except json.JSONDecodeError:
        # Try loading from file
        if os.path.exists(CUSTOM_PROVIDERS_JSON):
            with open(CUSTOM_PROVIDERS_JSON, 'r', encoding='utf-8') as f:
                CUSTOM_PROVIDERS = json.load(f)
        else:
            CUSTOM_PROVIDERS = {}

    # Application Settings
    MAX_DIFF_SIZE = 100000  # Maximum diff size in characters
    MAX_FILES_TO_REVIEW = 50  # Maximum number of files to review

    # Review Categories
    REVIEW_CATEGORIES = {
        'bugs': '潜在Bug和逻辑错误',
        'security': '安全漏洞和风险',
        'performance': '性能问题',
        'style': '代码风格和规范',
        'architecture': '架构和设计问题',
        'documentation': '文档和注释'
    }
