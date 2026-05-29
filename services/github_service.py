import re
import requests
from typing import Dict, List, Optional, Tuple
from config import Config


class GitHubService:
    """Service for interacting with GitHub API"""

    def __init__(self):
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AI-PR-Reviewer'
        }
        if Config.GITHUB_TOKEN:
            self.headers['Authorization'] = f'token {Config.GITHUB_TOKEN}'

    def parse_pr_url(self, pr_url: str) -> Optional[Tuple[str, str, int]]:
        """Parse GitHub PR URL to extract owner, repo, and PR number"""
        pattern = r'github\.com/([^/]+)/([^/]+)/pull/(\d+)'
        match = re.search(pattern, pr_url)
        if match:
            return match.group(1), match.group(2), int(match.group(3))
        return None

    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> Dict:
        """Get pull request information"""
        url = f'{Config.GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Get list of files changed in the PR"""
        url = f'{Config.GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files'
        all_files = []
        page = 1

        while True:
            response = requests.get(
                url,
                headers=self.headers,
                params={'page': page, 'per_page': 100}
            )
            response.raise_for_status()
            files = response.json()

            if not files:
                break

            all_files.extend(files)
            page += 1

            if len(all_files) >= Config.MAX_FILES_TO_REVIEW:
                all_files = all_files[:Config.MAX_FILES_TO_REVIEW]
                break

        return all_files

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Get the full diff of the PR"""
        url = f'{Config.GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}'
        headers = {**self.headers, 'Accept': 'application/vnd.github.v3.diff'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        diff = response.text
        if len(diff) > Config.MAX_DIFF_SIZE:
            diff = diff[:Config.MAX_DIFF_SIZE] + '\n... (diff truncated)'

        return diff

    def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> Optional[str]:
        """Get content of a specific file"""
        url = f'{Config.GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}'
        response = requests.get(url, headers=self.headers, params={'ref': ref})

        if response.status_code == 200:
            import base64
            content = response.json().get('content', '')
            return base64.b64decode(content).decode('utf-8', errors='ignore')
        return None

    def get_pr_comments(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Get review comments on the PR"""
        url = f'{Config.GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/comments'
        response = requests.get(url, headers=self.headers, params={'per_page': 100})
        response.raise_for_status()
        return response.json()

    def get_pr_commits(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Get commits in the PR"""
        url = f'{Config.GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/commits'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
