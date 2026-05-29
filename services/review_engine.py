import asyncio
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from services.github_service import GitHubService
from services.ai_service import AIService
from services.providers.factory import ProviderFactory
from config import Config


class ReviewEngine:
    """Main engine for orchestrating PR reviews"""

    def __init__(self, provider_name: Optional[str] = None, model: Optional[str] = None):
        self.github = GitHubService()
        self.ai = AIService(provider_name, model)
        self.executor = ThreadPoolExecutor(max_workers=4)

    def review_pr(self, pr_url: str) -> Dict:
        """Main entry point for reviewing a PR"""
        # Parse PR URL
        parsed = self.github.parse_pr_url(pr_url)
        if not parsed:
            return {
                'error': '无效的PR URL',
                'success': False
            }

        owner, repo, pr_number = parsed

        try:
            # Fetch PR data
            pr_info = self.github.get_pr_info(owner, repo, pr_number)
            files = self.github.get_pr_files(owner, repo, pr_number)
            diff = self.github.get_pr_diff(owner, repo, pr_number)

            # Perform AI analysis
            analysis = self.ai.analyze_pr(pr_info, diff, files)

            # Build response
            result = {
                'success': True,
                'pr_info': self._extract_pr_info(pr_info),
                'files_changed': self._extract_files_info(files),
                'analysis': analysis,
                'statistics': self._calculate_statistics(files)
            }

            return result

        except Exception as e:
            return {
                'error': f'获取PR数据失败: {str(e)}',
                'success': False
            }

    def _extract_pr_info(self, pr_info: Dict) -> Dict:
        """Extract relevant PR information"""
        return {
            'title': pr_info.get('title', ''),
            'number': pr_info.get('number', 0),
            'state': pr_info.get('state', ''),
            'author': pr_info.get('user', {}).get('login', ''),
            'created_at': pr_info.get('created_at', ''),
            'updated_at': pr_info.get('updated_at', ''),
            'base_branch': pr_info.get('base', {}).get('ref', ''),
            'head_branch': pr_info.get('head', {}).get('ref', ''),
            'description': pr_info.get('body', ''),
            'url': pr_info.get('html_url', ''),
            'additions': pr_info.get('additions', 0),
            'deletions': pr_info.get('deletions', 0),
            'changed_files': pr_info.get('changed_files', 0)
        }

    def _extract_files_info(self, files: List[Dict]) -> List[Dict]:
        """Extract relevant file information"""
        return [{
            'filename': f.get('filename', ''),
            'status': f.get('status', ''),
            'additions': f.get('additions', 0),
            'deletions': f.get('deletions', 0),
            'changes': f.get('changes', 0),
            'patch': f.get('patch', '')[:1000] if f.get('patch') else ''
        } for f in files]

    def _calculate_statistics(self, files: List[Dict]) -> Dict:
        """Calculate PR statistics"""
        total_additions = sum(f.get('additions', 0) for f in files)
        total_deletions = sum(f.get('deletions', 0) for f in files)

        file_types = {}
        for f in files:
            filename = f.get('filename', '')
            ext = filename.split('.')[-1] if '.' in filename else 'other'
            file_types[ext] = file_types.get(ext, 0) + 1

        return {
            'total_files': len(files),
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'total_changes': total_additions + total_deletions,
            'file_types': file_types
        }

    def get_file_deep_analysis(self, pr_url: str, filename: str) -> Dict:
        """Perform deep analysis on a specific file"""
        parsed = self.github.parse_pr_url(pr_url)
        if not parsed:
            return {'error': '无效的PR URL'}

        owner, repo, pr_number = parsed

        try:
            pr_info = self.github.get_pr_info(owner, repo, pr_number)
            head_sha = pr_info.get('head', {}).get('sha', '')

            content = self.github.get_file_content(owner, repo, filename, head_sha)
            if not content:
                return {'error': '无法获取文件内容'}

            analysis = self.ai.analyze_specific_issue(content, '全面')
            return analysis

        except Exception as e:
            return {'error': f'分析失败: {str(e)}'}
