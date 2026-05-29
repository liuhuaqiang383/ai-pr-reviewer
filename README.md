# AI PR Review 助手

一个基于Claude AI的智能代码评审工具，帮助开发者提升Pull Request的Review效率与质量。

## 功能特性

- **智能分析**: 使用Claude AI深度分析代码变更
- **风险评估**: 自动评估PR风险等级（低/中/高/严重）
- **问题检测**: 识别潜在Bug、安全漏洞、性能问题
- **改进建议**: 提供具体的代码改进建议
- **Review检查清单**: 自动生成审查检查项
- **变更总结**: 智能总结PR的整体变更

## 快速开始

### 1. 环境准备

确保已安装Python 3.8+：

```bash
python --version
```

### 2. 安装依赖

```bash
cd ai-pr-reviewer
pip install -r requirements.txt
```

### 3. 配置API密钥

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```env
# GitHub Token (可选，用于访问私有仓库)
GITHUB_TOKEN=your_github_token_here

# Claude API Key (必需)
CLAUDE_API_KEY=your_claude_api_key_here
```

**获取API密钥：**
- GitHub Token: https://github.com/settings/tokens
- Claude API Key: https://console.anthropic.com

### 4. 启动服务

```bash
python app.py
```

服务将在 http://localhost:5000 启动。

### 5. 使用工具

1. 在浏览器中打开 http://localhost:5000
2. 粘贴GitHub PR URL
3. 点击"开始分析"
4. 等待AI完成分析
5. 查看详细的审查报告

## 项目结构

```
ai-pr-reviewer/
├── app.py                 # Flask主应用
├── config.py             # 配置文件
├── requirements.txt      # Python依赖
├── .env.example         # 环境变量示例
├── services/
│   ├── __init__.py
│   ├── github_service.py  # GitHub API服务
│   ├── ai_service.py      # AI分析服务
│   └── review_engine.py   # 审查引擎
├── templates/
│   └── index.html         # 前端页面
├── static/
│   ├── style.css         # 样式文件
│   └── main.js          # 前端逻辑
├── README.md            # 项目说明
└── DESIGN.md           # 设计文档
```

## API接口

### 审查PR

```
POST /api/review
Content-Type: application/json

{
  "pr_url": "https://github.com/owner/repo/pull/123"
}
```

### 深度分析文件

```
POST /api/analyze-file
Content-Type: application/json

{
  "pr_url": "https://github.com/owner/repo/pull/123",
  "filename": "src/main.py"
}
```

### 健康检查

```
GET /api/health
```

## 配置说明

在 `config.py` 中可以调整以下配置：

- `MAX_DIFF_SIZE`: 最大diff大小（默认100KB）
- `MAX_FILES_TO_REVIEW`: 最大审查文件数（默认50）
- `CLAUDE_MODEL`: 使用的Claude模型

## 模型选择建议

| 模型 | 适用场景 | 特点 |
|------|----------|------|
| claude-haiku-4-20250514 | 快速审查 | 速度快，成本低 |
| claude-sonnet-4-20250514 | 日常审查 | 平衡速度和质量 |
| claude-opus-4-20250514 | 深度分析 | 最高质量，速度较慢 |

## 使用场景

1. **代码审查辅助**: 快速了解PR变更内容和潜在问题
2. **学习代码库**: 通过分析PR理解代码库结构
3. **质量把控**: 在合并前发现潜在问题
4. **知识分享**: 生成审查报告供团队参考

## 注意事项

- 仅支持GitHub平台的PR
- 私有仓库需要配置GitHub Token
- 大型PR可能需要较长分析时间
- AI分析结果仅供参考，最终决策需人工判断

## 扩展方向

- [ ] 支持GitLab、Bitbucket等平台
- [ ] 添加历史分析对比
- [ ] 集成CI/CD流水线
- [ ] 支持自定义审查规则
- [ ] 添加团队协作功能
- [ ] 生成PDF/HTML报告

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
