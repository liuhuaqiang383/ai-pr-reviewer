import requests
from typing import Dict, List, Optional
from config import Config


class GitHubCommentService:
    """Service for posting review comments to GitHub PRs"""

    def __init__(self):
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AI-PR-Reviewer',
            'Authorization': f'token {Config.GITHUB_TOKEN}'
        }

    def post_review_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        analysis: Dict,
        event: str = 'COMMENT'
    ) -> Dict:
        """
        Post a review comment to a PR

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number
            analysis: Analysis result from AI
            event: Review event type (APPROVE, REQUEST_CHANGES, COMMENT)
        """
        body = self._format_review_body(analysis)

        url = f'{Config.GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/reviews'

        payload = {
            'body': body,
            'event': event
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def post_inline_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        commit_sha: str,
        filename: str,
        line: int,
        body: str
    ) -> Dict:
        """Post an inline comment on a specific line"""
        url = f'{Config.GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/comments'

        payload = {
            'body': body,
            'commit_id': commit_sha,
            'path': filename,
            'line': line
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def post_issue_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str
    ) -> Dict:
        """Post a simple comment on the PR"""
        url = f'{Config.GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{pr_number}/comments'

        payload = {'body': body}

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def _format_review_body(self, analysis: Dict) -> str:
        """Format analysis result as Markdown for GitHub comment"""
        risk_level = analysis.get('risk_level', 'medium')
        risk_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }

        summary = analysis.get('summary', '无总结')
        issues = analysis.get('issues', [])
        suggestions = analysis.get('suggestions', [])
        highlights = analysis.get('highlights', [])
        checklist = analysis.get('checklist', [])
        provider = analysis.get('provider', 'AI')
        model = analysis.get('model', '')

        # Build the comment body
        lines = [
            '## 🤖 AI Code Review',
            '',
            f'**风险等级**: {risk_emoji.get(risk_level, "⚪")} {risk_level.upper()}',
            f'**分析模型**: {provider} ({model})',
            '',
            '### 📝 变更总结',
            summary,
            ''
        ]

        # Issues section
        if issues:
            lines.extend([
                '### ⚠️ 发现的问题',
                ''
            ])
            for issue in issues:
                severity = issue.get('severity', 'info')
                severity_emoji = {
                    'critical': '🔴',
                    'warning': '🟡',
                    'info': '🔵'
                }
                category = issue.get('category', '')
                file = issue.get('file', '')
                line_num = issue.get('line', '')
                desc = issue.get('description', '')
                suggestion = issue.get('suggestion', '')

                location = f'`{file}:{line_num}`' if file and line_num else f'`{file}`' if file else ''

                lines.append(f'- {severity_emoji.get(severity, "⚪")} **[{severity.upper()}]** {location} {desc}')
                if suggestion:
                    lines.append(f'  - 💡 *{suggestion}*')
            lines.append('')

        # Suggestions section
        if suggestions:
            lines.extend([
                '### 💡 改进建议',
                ''
            ])
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f'{i}. {suggestion}')
            lines.append('')

        # Highlights section
        if highlights:
            lines.extend([
                '### ✨ 代码亮点',
                ''
            ])
            for highlight in highlights:
                lines.append(f'- ⭐ {highlight}')
            lines.append('')

        # Checklist section
        if checklist:
            lines.extend([
                '### ✅ Review检查清单',
                ''
            ])
            for item in checklist:
                lines.append(f'- [ ] {item}')
            lines.append('')

        # Footer
        lines.extend([
            '',
            '---',
            f'<sub>🤖 由 AI PR Review 助手自动生成 | {provider} {model}</sub>'
        ])

        return '\n'.join(lines)

    def _format_inline_comment(self, issue: Dict) -> str:
        """Format an issue as an inline comment"""
        severity = issue.get('severity', 'info')
        severity_emoji = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🔵'
        }

        desc = issue.get('description', '')
        suggestion = issue.get('suggestion', '')

        lines = [
            f'{severity_emoji.get(severity, "⚪")} **[{severity.upper()}]** {desc}'
        ]

        if suggestion:
            lines.append(f'\n💡 **建议**: {suggestion}')

        lines.append(f'\n\n<sub>🤖 AI PR Review</sub>')

        return '\n'.join(lines)
