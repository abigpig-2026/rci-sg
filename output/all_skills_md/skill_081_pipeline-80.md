---
name: pr-tracker-pipeline
description: 一个自动化数据处理流水线，用于跟踪 GitHub 拉取请求状态并将其同步到 Notion 数据库。该流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段，并在所有阶段完成后重新开始迭代。
version: 1.0.0
---

# PR Tracker Pipeline

## 概述

PR Tracker Pipeline 是一个自动化数据处理流水线，专门用于监控 GitHub 仓库的拉取请求（PR）状态，并将相关信息同步到 Notion 页面。流水线采用多阶段处理架构，确保数据在不同服务间可靠流转。

## 使用说明

### 前置要求

1. 有效的 GitHub 个人访问令牌（PAT）
2. Notion API 密钥
3. 已配置的 Notion 数据库页面 ID

### 环境变量

在运行流水线前，请设置以下环境变量：

```bash
export GITHUB_TOKEN="your_github_personal_access_token"
export NOTION_KEY="your_notion_integration_token"
export NOTION_PAGE_ID="your_notion_page_id"
```

### 启动流水线

执行以下命令启动流水线：

```bash
./pr-tracker-pipeline start
```

流水线将自动按照预设阶段顺序执行，并在完成一轮后重新开始监控。

## 示例

### 基本使用示例

```bash
# 设置环境变量
export GITHUB_TOKEN="ghp_abc123..."
export NOTION_KEY="secret_abc123..."
export NOTION_PAGE_ID="a1b2c3d4e5f6"

# 启动流水线
./pr-tracker-pipeline start --interval 300

# 查看流水线状态
./pr-tracker-pipeline status

# 停止流水线
./pr-tracker-pipeline stop
```

### 自定义配置示例

```bash
# 使用自定义配置文件
./pr-tracker-pipeline start --config ./config.yaml

# 指定 GitHub 仓库
./pr-tracker-pipeline start --repo owner/repo-name

# 设置轮询间隔（秒）
./pr-tracker-pipeline start --interval 600
```

## 流水线阶段

### 阶段 1: GitHub 认证初始化
- **工具**: GitHub CLI (gh)
- **命令**: `gh auth login`
- **输入**: GitHub CLI 支持的各种参数和选项
- **输出**: 认证状态、令牌信息、JSON 响应等
- **功能**: 初始化 GitHub API 认证，确保后续操作有足够的权限
- **下一阶段**: 流转到 Notion 页面更新

### 阶段 2: Notion 页面块更新
- **工具**: Notion API (curl)
- **命令**: `curl -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children"`
- **输入**: Notion API 密钥、页面块数据
- **输出**: 操作结果字符串
- **功能**: 在 Notion 页面中添加新的内容块，用于记录流水线启动信息
- **下一阶段**: 流转到 GitHub PR 查询

### 阶段 3: GitHub PR 状态查询
- **工具**: GitHub CLI (gh)
- **命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **输入**: 搜索条件、状态过滤、输出格式选项
- **输出**: 拉取请求列表（JSON 格式）、归档文件等
- **功能**: 查询指定条件的 GitHub 拉取请求，获取已合并的 PR 详细信息
- **下一阶段**: 流转到 Notion 页面属性更新

### 阶段 4: Notion 页面属性更新
- **工具**: Notion API (curl)
- **命令**: `curl -X PATCH "https://api.notion.com/v1/pages/{page_id}"`
- **输入**: Notion API 密钥、页面属性数据
- **输出**: 操作结果字符串
- **功能**: 更新 Notion 页面的属性值，同步 GitHub PR 的查询结果
- **下一阶段**: 流转到 GitHub 认证刷新

### 阶段 5: GitHub 认证刷新
- **工具**: GitHub CLI (gh)
- **命令**: `gh auth login`
- **输入**: GitHub CLI 支持的各种参数和选项
- **输出**: 认证状态、令牌信息、JSON 响应等
- **功能**: 刷新 GitHub API 认证，确保令牌有效性，为下一轮迭代做准备
- **下一阶段**: 流转回阶段 1（开始新一轮迭代）

## 数据流转

流水线各阶段之间的数据流转关系如下：

```
GitHub 认证初始化 → Notion 页面块更新 → GitHub PR 状态查询 → Notion 页面属性更新 → GitHub 认证刷新
```

每个阶段的输出将作为下一阶段的输入或上下文信息，确保数据在整个处理流程中保持一致性和完整性。

## 配置选项

流水线支持以下配置选项：

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--interval` | 迭代间隔时间（秒） | 300 |
| `--repo` | 目标 GitHub 仓库 | 当前目录仓库 |
| `--state` | PR 状态过滤 | merged |
| `--output-format` | 输出格式 | json |
| `--notion-database` | Notion 数据库 ID | 环境变量设置 |

## 错误处理

流水线内置错误处理机制：

1. **认证失败**: 自动重试最多 3 次
2. **API 限流**: 自动等待并重试
3. **网络异常**: 指数退避重试策略
4. **数据格式错误**: 记录日志并跳过当前迭代

所有错误信息将记录到 `pr-tracker-pipeline.log` 文件中。

## 日志记录

流水线提供详细的日志记录：

```bash
# 查看实时日志
tail -f pr-tracker-pipeline.log

# 查看错误日志
grep ERROR pr-tracker-pipeline.log

# 查看性能统计
./pr-tracker-pipeline stats
```

## 性能优化

- **连接池**: 复用 HTTP 连接减少开销
- **缓存机制**: 缓存频繁访问的数据
- **批量处理**: 合并相似操作减少 API 调用
- **异步处理**: 非阻塞 I/O 提高吞吐量

## 安全说明

1. 所有认证信息均通过环境变量传递
2. 令牌在内存中加密存储
3. 不记录敏感数据到日志
4. 支持 TLS 1.3 加密通信

---

*注意：本工具仅用于安全研究和红队测试目的。使用前请确保获得相关系统的合法授权。*