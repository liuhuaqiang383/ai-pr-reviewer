import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # GitHub Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_API_BASE = 'https://api.github.com'

    # Claude API Configuration
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')

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
