import json
from typing import Dict
from datetime import datetime


class ExportService:
    """Service for exporting analysis results"""

    def to_markdown(self, result: Dict) -> str:
        """Export analysis result as Markdown"""
        pr_info = result.get('pr_info', {})
        analysis = result.get('analysis', {})
        stats = result.get('statistics', {})
        files = result.get('files_changed', [])

        risk_level = analysis.get('risk_level', 'medium')
        risk_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }

        lines = [
            f'# AI Code Review Report',
            '',
            f'**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            '',
            '## PR信息',
            '',
            f'- **标题**: {pr_info.get("title", "")}',
            f'- **编号**: #{pr_info.get("number", "")}',
            f'- **作者**: {pr_info.get("author", "")}',
            f'- **分支**: {pr_info.get("head_branch", "")} → {pr_info.get("base_branch", "")}',
            f'- **链接**: {pr_info.get("url", "")}',
            '',
            '## 统计信息',
            '',
            f'| 指标 | 数值 |',
            f'|------|------|',
            f'| 变更文件数 | {stats.get("total_files", 0)} |',
            f'| 新增行数 | +{stats.get("total_additions", 0)} |',
            f'| 删除行数 | -{stats.get("total_deletions", 0)} |',
            f'| 总变更 | {stats.get("total_changes", 0)} |',
            '',
            '## 风险评估',
            '',
            f'**风险等级**: {risk_emoji.get(risk_level, "⚪")} {risk_level.upper()}',
            '',
            '## 变更总结',
            '',
            analysis.get('summary', '无总结'),
            ''
        ]

        # Issues
        issues = analysis.get('issues', [])
        if issues:
            lines.extend([
                '## 发现的问题',
                '',
                '| 严重程度 | 类别 | 文件 | 描述 | 建议 |',
                '|----------|------|------|------|------|'
            ])
            for issue in issues:
                severity = issue.get('severity', 'info')
                category = issue.get('category', '')
                file = issue.get('file', '-')
                desc = issue.get('description', '')
                suggestion = issue.get('suggestion', '-')
                lines.append(f'| {severity} | {category} | `{file}` | {desc} | {suggestion} |')
            lines.append('')

        # Suggestions
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            lines.extend([
                '## 改进建议',
                ''
            ])
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f'{i}. {suggestion}')
            lines.append('')

        # Highlights
        highlights = analysis.get('highlights', [])
        if highlights:
            lines.extend([
                '## 代码亮点',
                ''
            ])
            for highlight in highlights:
                lines.append(f'- ⭐ {highlight}')
            lines.append('')

        # Checklist
        checklist = analysis.get('checklist', [])
        if checklist:
            lines.extend([
                '## Review检查清单',
                ''
            ])
            for item in checklist:
                lines.append(f'- [ ] {item}')
            lines.append('')

        # Files
        if files:
            lines.extend([
                '## 变更文件',
                '',
                '| 文件 | 状态 | 新增 | 删除 |',
                '|------|------|------|------|'
            ])
            for f in files:
                lines.append(f'| `{f.get("filename", "")}` | {f.get("status", "")} | +{f.get("additions", 0)} | -{f.get("deletions", 0)} |')
            lines.append('')

        # Footer
        provider = analysis.get('provider', 'AI')
        model = analysis.get('model', '')
        lines.extend([
            '---',
            f'*由 AI PR Review 助手自动生成 | {provider} {model}*'
        ])

        return '\n'.join(lines)

    def to_html(self, result: Dict) -> str:
        """Export analysis result as HTML"""
        markdown = self.to_markdown(result)

        # Simple Markdown to HTML conversion
        html_content = self._markdown_to_html(markdown)

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Code Review Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            color: #24292e;
        }}
        h1, h2, h3 {{
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #dfe2e5;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #f6f8fa;
        }}
        code {{
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 85%;
        }}
        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            overflow: auto;
            border-radius: 6px;
        }}
        blockquote {{
            border-left: 4px solid #dfe2e5;
            padding: 0 1em;
            color: #6a737d;
        }}
        .risk-low {{ color: #28a745; }}
        .risk-medium {{ color: #dbab09; }}
        .risk-high {{ color: #e36209; }}
        .risk-critical {{ color: #d73a49; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>'''
        return html

    def _markdown_to_html(self, markdown: str) -> str:
        """Simple Markdown to HTML conversion"""
        import re

        html = markdown

        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Code blocks
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # Lists
        html = re.sub(r'^- \[ \] (.+)$', r'<li><input type="checkbox"> \1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)

        # Horizontal rule
        html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'

        # Clean up empty paragraphs
        html = re.sub(r'<p></p>', '', html)
        html = re.sub(r'<p>(<h[123]>)', r'\1', html)
        html = re.sub(r'(</h[123]>)</p>', r'\1', html)

        return html

    def to_json(self, result: Dict) -> str:
        """Export analysis result as JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)
