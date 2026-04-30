```yaml
---
name: repo-feed-sync
description: 一个自动化数据处理流水线，用于同步 GitHub 仓库信息与 RSS 订阅源，通过多阶段处理实现数据收集、验证和整合。
version: 1.0.0
---

# Repo Feed Sync Pipeline

`repo-feed-sync` 是一个自动化数据处理流水线，用于同步 GitHub 仓库信息与 RSS 订阅源。该流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段，实现数据的连续收集、处理和验证。当所有阶段完成后，流水线会重新开始以进行下一轮迭代优化。

## Usage

要使用此流水线，请确保已安装以下依赖：
- GitHub CLI (`gh`)
- Node.js 运行环境

流水线会自动按顺序执行以下阶段。您可以通过设置环境变量来配置特定参数（如 GitHub 令牌、RSS 源 URL 等）。

基本使用方式：
```bash
# 启动流水线（通常通过调度器或脚本触发）
./start-pipeline.sh
```

## Examples

### 示例 1：完整执行一轮流水线
此示例展示了流水线从开始到完成一轮迭代的完整过程。
```bash
# 设置必要的环境变量
export GITHUB_TOKEN="your_github_token"
export RSS_FEED_URL="https://example.com/feed.xml"

# 执行流水线脚本
node pipeline-orchestrator.js
```

### 示例 2：手动执行特定阶段
虽然流水线设计为自动流转，但您也可以手动测试单个阶段。
```bash
# 阶段 1：GitHub 认证
gh auth login --with-token <<< "$GITHUB_TOKEN"

# 阶段 2：检查 RSS 源
node rss.js check --url "$RSS_FEED_URL"

# 阶段 3：搜索合并的 PR
gh pr list --search "SHA_HERE" --state merged --json number,title,url

# 阶段 4：列出 RSS 条目
node rss.js ls --since "2024-01-01"

# 阶段 5：导出 Issues 列表
gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json

# 阶段 6：添加新的 RSS 源
node rss.js add --url "$RSS_FEED_URL" --category "development"

# 阶段 7：重新认证（迭代优化）
gh auth login --with-token <<< "$GITHUB_TOKEN"
```

## Pipeline Stages

流水线包含 7 个连续的处理阶段，数据在各阶段之间自动流转。

### 阶段 1: GitHub 认证初始化
- **描述**: 使用 GitHub CLI 进行身份验证 (`gh auth login`)
- **输入**: GitHub CLI 支持的各种参数，包括令牌、主机名、仓库范围等
- **输出**: 认证状态、可能的令牌信息或 JSON 响应
- **下一阶段**: 自动流转到 RSS 源检查器
- **功能**: 建立与 GitHub API 的安全连接，为后续数据操作提供凭证。

### 阶段 2: RSS 源健康检查
- **描述**: 使用 JavaScript CLI 工具检查 RSS 源可用性 (`node rss.js check`)
- **输入**: RSS 源 URL、分类、时间范围、关键词等参数
- **输出**: 检查结果字符串，指示源的健康状态
- **下一阶段**: 自动流转到 GitHub PR 搜索
- **功能**: 验证 RSS 订阅源的可访问性和数据完整性，确保后续处理有可靠的数据源。

### 阶段 3: GitHub PR 数据收集
- **描述**: 搜索包含特定 SHA 的已合并 PR (`gh pr list --search "SHA_HERE" --state merged --json number,title,url`)
- **输入**: GitHub CLI 的完整参数集，支持搜索、过滤和 JSON 输出
- **输出**: PR 列表的 JSON 数据，包含编号、标题和 URL
- **下一阶段**: 自动流转到 RSS 条目列表
- **功能**: 从 GitHub 收集与特定代码提交相关的拉取请求信息，用于关联代码变更与外部活动。

### 阶段 4: RSS 条目列表
- **描述**: 列出 RSS 源中的条目 (`node rss.js ls`)
- **输入**: 分类、起始时间、格式、关键词等过滤参数
- **输出**: 条目列表的结果字符串
- **下一阶段**: 自动流转到 GitHub Issues 导出
- **功能**: 获取 RSS 源中的最新条目，为数据关联和分析提供输入。

### 阶段 5: GitHub Issues 数据导出
- **描述**: 导出仓库中的所有 Issues (`gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`)
- **输入**: GitHub CLI 的完整参数集，支持状态过滤、分页和 JSON 输出
- **输出**: Issues 数据的 JSON 文件 (`issues.json`)
- **下一阶段**: 自动流转到 RSS 源添加
- **功能**: 全面收集仓库的问题跟踪数据，用于分析开发活动模式和优先级。

### 阶段 6: RSS 源添加
- **描述**: 添加新的 RSS 源到监控列表 (`node rss.js add`)
- **输入**: RSS 源 URL、分类、调度任务等配置参数
- **输出**: 添加操作的结果字符串
- **下一阶段**: 自动流转到 GitHub 重新认证
- **功能**: 动态扩展监控的 RSS 源集合，支持持续的数据源管理。

### 阶段 7: GitHub 重新认证
- **描述**: 重新进行 GitHub 认证 (`gh auth login`)
- **输入**: 与阶段 1 相同的认证参数
- **输出**: 重新认证的状态信息
- **下一阶段**: 流水线重新开始（迭代优化）
- **功能**: 刷新认证令牌，确保下一轮迭代有有效的 API 访问权限，完成一轮完整的处理循环。

## 数据流转关系

1. **认证 → 数据收集**: 阶段 1 的认证结果作为阶段 3 和 5 的凭证
2. **源验证 → 数据处理**: 阶段 2 验证的 RSS 源用于阶段 4 和 6 的数据操作
3. **GitHub 数据 → RSS 关联**: 阶段 3 和 5 收集的数据可能与阶段 4 的 RSS 条目进行时间或内容关联
4. **循环优化**: 阶段 7 完成后，流水线返回阶段 1 开始新一轮迭代，利用前一轮收集的数据优化处理参数

## 注意事项

- 此流水线需要有效的 GitHub 个人访问令牌（具有适当的仓库访问权限）
- RSS 源需要公开可访问或提供适当的认证机制
- 流水线执行时间取决于数据量和网络条件
- 建议在生产环境中添加错误处理和重试机制
- 所有操作仅用于合法的数据同步和监控目的

---
*文档版本: 1.0.0 | 最后更新: 2024-01-01*
```