from typing import Dict, List, Optional
from config import Config
from services.providers.factory import ProviderFactory


class AIService:
    """Service for AI-powered code analysis"""

    def __init__(self, provider_name: Optional[str] = None, model: Optional[str] = None):
        self.provider = ProviderFactory.create_provider(provider_name, model)

    def analyze_pr(self, pr_info: Dict, diff: str, files: List[Dict]) -> Dict:
        """Perform comprehensive PR analysis"""
        prompt = self._build_analysis_prompt(pr_info, diff, files)

        try:
            analysis_text = self.provider.analyze(prompt, max_tokens=4096)
            result = self._parse_analysis(analysis_text)
            # Add provider info to result
            result['provider'] = self.provider.get_provider_name()
            result['model'] = self.provider.get_model_name()
            return result

        except Exception as e:
            return {
                'error': str(e),
                'summary': '分析过程中出现错误',
                'issues': [],
                'suggestions': []
            }

    def _build_analysis_prompt(self, pr_info: Dict, diff: str, files: List[Dict]) -> str:
        """Build the analysis prompt for Claude"""
        title = pr_info.get('title', 'Unknown')
        description = pr_info.get('body', 'No description')
        author = pr_info.get('user', {}).get('login', 'Unknown')
        base_branch = pr_info.get('base', {}).get('ref', 'main')
        head_branch = pr_info.get('head', {}).get('ref', 'unknown')

        files_summary = self._summarize_files(files)

        prompt = f"""你是一个专业的代码审查专家。请分析以下GitHub Pull Request并提供详细的审查意见。

## PR信息
- 标题: {title}
- 作者: {author}
- 目标分支: {base_branch} <- {head_branch}
- 描述: {description}

## 变更文件概览
{files_summary}

## 代码变更 (Diff)
```diff
{diff[:30000]}
```

请提供以下分析（使用JSON格式返回）：

1. **summary**: PR的整体总结（2-3句话）
2. **risk_level**: 风险等级（low/medium/high/critical）
3. **issues**: 发现的问题列表，每个问题包含：
   - severity: 严重程度（info/warning/error/critical）
   - category: 类别（bug/security/performance/style/architecture/documentation）
   - file: 相关文件
   - line: 行号（如果能确定）
   - description: 问题描述
   - suggestion: 修复建议
4. **suggestions**: 整体改进建议列表
5. **highlights**: 代码亮点（如果有的话）
6. **checklist**: Review检查清单

请用中文回复，确保分析准确且有建设性。重点关注：
- 潜在的Bug和逻辑错误
- 安全漏洞
- 性能问题
- 代码可维护性
- 测试覆盖
"""

        return prompt

    def _summarize_files(self, files: List[Dict]) -> str:
        """Summarize changed files"""
        if not files:
            return "无文件变更信息"

        summary_lines = []
        for f in files[:20]:  # Limit to first 20 files
            filename = f.get('filename', 'unknown')
            status = f.get('status', 'modified')
            additions = f.get('additions', 0)
            deletions = f.get('deletions', 0)
            summary_lines.append(f"- {filename} ({status}): +{additions}/-{deletions}")

        if len(files) > 20:
            summary_lines.append(f"... 还有 {len(files) - 20} 个文件")

        return '\n'.join(summary_lines)

    def _parse_analysis(self, analysis_text: str) -> Dict:
        """Parse the AI analysis response"""
        import json
        import re

        # Try to extract JSON from the response
        json_match = re.search(r'\{[\s\S]*\}', analysis_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback: return structured text
        return {
            'summary': analysis_text[:500],
            'risk_level': 'medium',
            'issues': [],
            'suggestions': [analysis_text],
            'highlights': [],
            'checklist': []
        }

    def analyze_specific_issue(self, code_context: str, issue_type: str) -> Dict:
        """Deep dive analysis for a specific code section"""
        prompt = f"""请深入分析以下代码片段，重点关注{issue_type}问题：

```
{code_context}
```

请提供：
1. 问题详细描述
2. 影响范围
3. 修复方案（包含代码示例）
4. 预防措施
"""

        try:
            analysis_text = self.provider.analyze(prompt, max_tokens=2048)

            return {
                'analysis': analysis_text,
                'issue_type': issue_type,
                'provider': self.provider.get_provider_name(),
                'model': self.provider.get_model_name()
            }

        except Exception as e:
            return {
                'error': str(e),
                'analysis': '分析失败'
            }
