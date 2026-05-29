# AI PR Review 助手

一个支持**任意AI模型**的智能代码评审工具，帮助开发者提升Pull Request的Review效率与质量。

## 功能特性

- **多模型支持**: 支持OpenAI、Claude、Gemini、DeepSeek、Moonshot、智谱、通义千问等主流AI，以及Ollama等本地模型
- **自由配置**: 可通过环境变量、JSON配置或前端界面任意添加AI提供商
- **智能分析**: 深度分析代码变更，识别潜在问题
- **风险评估**: 自动评估PR风险等级（低/中/高/严重）
- **问题检测**: 识别潜在Bug、安全漏洞、性能问题
- **改进建议**: 提供具体的代码改进建议
- **Review检查清单**: 自动生成审查检查项
- **变更总结**: 智能总结PR的整体变更
- **GitHub评论**: 分析结果直接评论到GitHub PR
- **流式输出**: 实时显示分析进度
- **智能缓存**: 避免重复分析，24小时自动过期
- **结果导出**: 支持Markdown/HTML/JSON格式导出

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

### 3. 配置AI模型

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你要使用的AI提供商：

```env
# 选择默认AI提供商和模型
DEFAULT_AI_PROVIDER=openai
DEFAULT_AI_MODEL=your-model-name

# 配置对应的API Key
OPENAI_API_KEY=your-api-key
```

**内置提供商环境变量：**

| 提供商 | 环境变量 |
|--------|----------|
| OpenAI | `OPENAI_API_KEY` |
| Claude | `CLAUDE_API_KEY` |
| Gemini | `GEMINI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Moonshot | `MOONSHOT_API_KEY` |
| 智谱AI | `ZHIPU_API_KEY` |
| 通义千问 | `QWEN_API_KEY` |

> 本地模型（如Ollama）通常不需要API Key。

### 4. 启动服务

```bash
python app.py
```

服务将在 http://localhost:5000 启动。

### 5. 使用工具

1. 在浏览器中打开 http://localhost:5000
2. 粘贴GitHub PR URL
3. 选择AI提供商和模型
4. 点击"开始分析"
5. 等待AI完成分析
6. 查看详细的审查报告

## 项目结构

```
ai-pr-reviewer/
├── app.py                      # Flask主应用
├── config.py                   # 配置文件
├── requirements.txt            # Python依赖
├── .env.example                # 环境变量示例
├── custom_providers.example.json # 自定义提供商配置示例
├── services/
│   ├── __init__.py
│   ├── github_service.py       # GitHub API服务
│   ├── ai_service.py           # AI分析服务
│   ├── review_engine.py        # 审查引擎
│   └── providers/
│       ├── __init__.py
│       ├── base.py             # Provider基类
│       ├── openai_compatible.py # OpenAI兼容Provider
│       ├── anthropic_compatible.py # Anthropic兼容Provider
│       ├── custom_provider.py  # 自定义格式Provider
│       └── factory.py          # Provider工厂
├── templates/
│   └── index.html              # 前端页面
├── static/
│   ├── style.css               # 样式文件
│   └── main.js                 # 前端逻辑
├── README.md                   # 项目说明
└── DESIGN.md                   # 设计文档
```

## 自定义AI提供商

除了内置的AI提供商，你可以添加任意自定义模型：

### 方式1: 环境变量配置

在 `.env` 文件中添加JSON配置：

```env
CUSTOM_PROVIDERS={"my-llm": {"name": "我的模型", "type": "openai_compatible", "base_url": "http://localhost:11434/v1", "model": "llama3"}}
```

### 方式2: JSON配置文件

创建 `custom_providers.json`：

```json
{
  "my-local-llm": {
    "name": "本地Ollama",
    "type": "openai_compatible",
    "base_url": "http://localhost:11434/v1",
    "api_key": "",
    "model": "llama3"
  },
  "company-api": {
    "name": "公司内部API",
    "type": "openai_compatible",
    "base_url": "https://api.company.com/v1",
    "api_key": "sk-xxx",
    "model": "company-model"
  }
}
```

然后在 `.env` 中指向该文件：

```env
CUSTOM_PROVIDERS=./custom_providers.json
```

### 方式3: 前端界面配置

1. 打开 http://localhost:5000
2. 在AI提供商下拉框选择"自定义配置"
3. 填写API地址、Key、模型名
4. 点击"测试连接"验证
5. 点击"应用"开始使用

## API接口

### 审查PR

```
POST /api/review
Content-Type: application/json

{
  "pr_url": "https://github.com/owner/repo/pull/123",
  "provider": "openai",        // 可选，默认使用配置的提供商
  "model": "gpt-4o"           // 可选，默认使用配置的模型
}
```

**使用自定义配置：**

```json
{
  "pr_url": "https://github.com/owner/repo/pull/123",
  "custom_config": {
    "name": "My LLM",
    "type": "openai_compatible",
    "base_url": "http://localhost:11434/v1",
    "model": "llama3"
  }
}
```

### 获取可用提供商

```
GET /api/providers
```

### 测试提供商连接

```
POST /api/providers/test
Content-Type: application/json

{
  "provider": "openai",
  "model": "gpt-4o"
}
```

### 流式分析 (Server-Sent Events)

```
POST /api/review/stream
Content-Type: application/json

{
  "pr_url": "https://github.com/owner/repo/pull/123",
  "provider": "openai",
  "model": "gpt-4o"
}

# 响应格式 (SSE):
# data: {"type": "progress", "step": 1, "message": "获取PR信息..."}
# data: {"type": "pr_info", "data": {...}}
# data: {"type": "progress", "step": 2, "message": "获取变更文件..."}
# data: {"type": "complete", "data": {...}}
```

### 发布评论到GitHub PR

```
POST /api/comment
Content-Type: application/json

{
  "pr_url": "https://github.com/owner/repo/pull/123",
  "analysis": { ... },  // 分析结果
  "type": "review",      // review 或 comment
  "provider": "openai",
  "model": "gpt-4o"
}
```

### 导出分析结果

```
POST /api/export
Content-Type: application/json

{
  "result": { ... },     // 完整分析结果
  "format": "markdown",  // markdown, html, json
  "provider": "openai",
  "model": "gpt-4o"
}

# 响应: 文件下载
```

### 缓存统计

```
GET /api/cache/stats

# 响应:
# {
#   "total": 10,
#   "size_bytes": 102400,
#   "size_mb": 0.1
# }
```

### 清理缓存

```
POST /api/cache/clear
Content-Type: application/json

{
  "older_than_hours": 24  // 清理超过24小时的缓存
}
```

### 深度分析文件

```
POST /api/analyze-file
Content-Type: application/json

{
  "pr_url": "https://github.com/owner/repo/pull/123",
  "filename": "src/main.py",
  "provider": "claude",
  "model": "claude-sonnet-4-20250514"
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
- `DEFAULT_AI_PROVIDER`: 默认AI提供商
- `DEFAULT_AI_MODEL`: 默认模型

## 支持的AI提供商

系统支持任意兼容OpenAI或Anthropic API格式的AI服务，包括但不限于：

- **云服务**: OpenAI, Claude, Gemini, DeepSeek, Moonshot, 智谱AI, 通义千问等
- **本地模型**: Ollama, LM Studio, vLLM等
- **私有部署**: 任何兼容OpenAI API格式的自建服务

用户可在配置文件或前端界面中自行填写API地址、密钥和模型名称。

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
