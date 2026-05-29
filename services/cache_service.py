import os
import json
import hashlib
from typing import Dict, Optional
from datetime import datetime, timedelta
from config import Config


class CacheService:
    """Service for caching analysis results"""

    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_key(self, pr_url: str, provider: str, model: str) -> str:
        """Generate cache key from PR URL and provider info"""
        key_string = f"{pr_url}:{provider}:{model}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, pr_url: str, provider: str, model: str) -> Optional[Dict]:
        """Get cached analysis result"""
        cache_key = self._get_cache_key(pr_url, provider, model)
        cache_path = self._get_cache_path(cache_key)

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # Check if cache is expired (24 hours)
            cached_time = datetime.fromisoformat(cache_data.get('cached_at', ''))
            if datetime.now() - cached_time > timedelta(hours=24):
                os.remove(cache_path)
                return None

            return cache_data.get('result')

        except (json.JSONDecodeError, ValueError):
            # Invalid cache file, remove it
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None

    def set(self, pr_url: str, provider: str, model: str, result: Dict):
        """Cache analysis result"""
        cache_key = self._get_cache_key(pr_url, provider, model)
        cache_path = self._get_cache_path(cache_key)

        cache_data = {
            'pr_url': pr_url,
            'provider': provider,
            'model': model,
            'cached_at': datetime.now().isoformat(),
            'result': result
        }

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    def clear(self, older_than_hours: int = 24):
        """Clear expired cache entries"""
        if not os.path.exists(self.cache_dir):
            return

        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)

        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(self.cache_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                cached_time = datetime.fromisoformat(cache_data.get('cached_at', ''))
                if cached_time < cutoff_time:
                    os.remove(filepath)

            except (json.JSONDecodeError, ValueError):
                os.remove(filepath)

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not os.path.exists(self.cache_dir):
            return {'total': 0, 'size_bytes': 0}

        total = 0
        size_bytes = 0

        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                total += 1
                size_bytes += os.path.getsize(filepath)

        return {
            'total': total,
            'size_bytes': size_bytes,
            'size_mb': round(size_bytes / (1024 * 1024), 2)
        }
