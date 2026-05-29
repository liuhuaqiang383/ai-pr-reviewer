import asyncio
from typing import Dict, List, Optional, Any, Generator
from concurrent.futures import ThreadPoolExecutor
from services.github_service import GitHubService
from services.ai_service import AIService
from services.github_comment import GitHubCommentService
from services.cache_service import CacheService
from services.export_service import ExportService
from services.providers.factory import ProviderFactory
from config import Config


class ReviewEngine:
    """Main engine for orchestrating PR reviews"""

    def __init__(
        self,
        provider_id: Optional[str] = None,
        model: Optional[str] = None,
        custom_config: Optional[Dict] = None
    ):
        self.github = GitHubService()
        self.ai = AIService(provider_id, model, custom_config)
        self.comment_service = GitHubCommentService()
        self.cache_service = CacheService()
        self.export_service = ExportService()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def review_pr(self, pr_url: str, use_cache: bool = True) -> Dict:
        """Main entry point for reviewing a PR"""
        # Parse PR URL
        parsed = self.github.parse_pr_url(pr_url)
        if not parsed:
            return {
                'error': '无效的PR URL',
                'success': False
            }

        owner, repo, pr_number = parsed

        # Check cache first
        if use_cache:
            provider_name = self.ai.provider.get_provider_name()
            model_name = self.ai.provider.get_model_name()
            cached = self.cache_service.get(pr_url, provider_name, model_name)
            if cached:
                cached['from_cache'] = True
                return cached

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
                'statistics': self._calculate_statistics(files),
                'from_cache': False
            }

            # Cache the result
            provider_name = self.ai.provider.get_provider_name()
            model_name = self.ai.provider.get_model_name()
            self.cache_service.set(pr_url, provider_name, model_name, result)

            return result

        except Exception as e:
            return {
                'error': f'获取PR数据失败: {str(e)}',
                'success': False
            }

    def review_pr_stream(self, pr_url: str) -> Generator[Dict, None, None]:
        """Stream review progress"""
        parsed = self.github.parse_pr_url(pr_url)
        if not parsed:
            yield {'type': 'error', 'message': '无效的PR URL'}
            return

        owner, repo, pr_number = parsed

        try:
            # Step 1: Fetch PR info
            yield {'type': 'progress', 'step': 1, 'message': '获取PR信息...'}
            pr_info = self.github.get_pr_info(owner, repo, pr_number)
            yield {'type': 'pr_info', 'data': self._extract_pr_info(pr_info)}

            # Step 2: Fetch files
            yield {'type': 'progress', 'step': 2, 'message': '获取变更文件...'}
            files = self.github.get_pr_files(owner, repo, pr_number)
            yield {'type': 'files', 'data': self._extract_files_info(files)}

            # Step 3: Fetch diff
            yield {'type': 'progress', 'step': 3, 'message': '获取代码差异...'}
            diff = self.github.get_pr_diff(owner, repo, pr_number)

            # Step 4: AI Analysis
            yield {'type': 'progress', 'step': 4, 'message': 'AI分析中...'}
            analysis = self.ai.analyze_pr(pr_info, diff, files)
            yield {'type': 'analysis', 'data': analysis}

            # Complete
            result = {
                'success': True,
                'pr_info': self._extract_pr_info(pr_info),
                'files_changed': self._extract_files_info(files),
                'analysis': analysis,
                'statistics': self._calculate_statistics(files)
            }

            # Cache the result
            provider_name = self.ai.provider.get_provider_name()
            model_name = self.ai.provider.get_model_name()
            self.cache_service.set(pr_url, provider_name, model_name, result)

            yield {'type': 'complete', 'data': result}

        except Exception as e:
            yield {'type': 'error', 'message': str(e)}

    def post_comment(self, pr_url: str, analysis: Dict, comment_type: str = 'review') -> Dict:
        """Post analysis result as comment to GitHub PR"""
        parsed = self.github.parse_pr_url(pr_url)
        if not parsed:
            return {'error': '无效的PR URL'}

        owner, repo, pr_number = parsed

        try:
            if comment_type == 'review':
                result = self.comment_service.post_review_comment(
                    owner, repo, pr_number, analysis
                )
            else:
                body = self.comment_service._format_review_body(analysis)
                result = self.comment_service.post_issue_comment(
                    owner, repo, pr_number, body
                )

            return {'success': True, 'comment_url': result.get('html_url', '')}

        except Exception as e:
            return {'error': f'评论失败: {str(e)}'}

    def export_result(self, result: Dict, format: str = 'markdown') -> str:
        """Export analysis result"""
        if format == 'markdown':
            return self.export_service.to_markdown(result)
        elif format == 'html':
            return self.export_service.to_html(result)
        elif format == 'json':
            return self.export_service.to_json(result)
        else:
            raise ValueError(f'不支持的导出格式: {format}')

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache_service.get_stats()

    def clear_cache(self, older_than_hours: int = 24):
        """Clear expired cache"""
        self.cache_service.clear(older_than_hours)

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
