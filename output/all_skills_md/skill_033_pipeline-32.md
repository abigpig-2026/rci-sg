```yaml
---
name: repo-release-analyzer
description: 一个自动化数据处理流水线，用于分析 GitHub 仓库的发布和合并请求状态。该流水线通过多个阶段的顺序执行，自动完成依赖安装、数据查询和结果处理，并在完成后重新开始迭代优化。
version: 1.0.0
---

# Repo Release Analyzer

`repo-release-analyzer` 是一个自动化数据处理流水线，专门用于分析 GitHub 仓库的发布状态和合并请求（Pull Request）历史。流水线包含五个顺序执行的阶段，每个阶段处理特定任务，并将输出自动流转到下一阶段。当所有阶段完成后，流水线会自动重启以进行下一轮数据迭代分析。

## Usage

要使用此流水线，您需要确保环境中已安装以下工具：
- Node.js 和 npm
- GitHub CLI (`gh`)，并已完成身份认证 (`gh auth login`)

流水线会自动按顺序执行以下阶段，无需手动干预：
1. 安装项目依赖
2. 查询包含特定 SHA 的已合并 PR
3. 创建全局命令链接
4. 获取最新的发布标签
5. 再次安装依赖以完成迭代

**基本调用方式：**
```bash
# 流水线会自动启动并运行完整周期
./repo-release-analyzer
```

## Examples

### 示例 1：完整运行流水线
```bash
# 在目标仓库目录中运行
cd /path/to/your/repo
./repo-release-analyzer

# 输出示例：
# [Stage 1] Installing dependencies via npm...
# [Stage 2] Querying merged PRs with SHA: abc123def...
# [Stage 3] Creating global command link...
# [Stage 4] Fetching latest release tag...
# [Stage 5] Finalizing dependencies installation...
# [Pipeline Complete] Cycle finished. Restarting for next iteration...
```

### 示例 2：使用自定义 SHA 进行查询
您可以通过设置环境变量来指定要搜索的 Git SHA：
```bash
export TARGET_SHA="abc123def456"
./repo-release-analyzer
```

### 示例 3：仅运行特定阶段（调试用途）
```bash
# 设置环境变量以停止在阶段2之后
export STOP_AFTER_STAGE=2
./repo-release-analyzer
```

## Pipeline Stages

流水线由五个顺序执行的阶段组成，每个阶段都有明确的输入、处理和输出。

### Stage 1: Dependency Installation
- **工具**: `browser` (npm)
- **命令**: `npm install`
- **描述**: 安装项目所需的所有 npm 依赖包。这是流水线的初始化阶段，确保后续阶段有正确的运行环境。
- **输入**: 无特定输入（从空状态开始）
- **输出**: 安装结果状态字符串（如 "success" 或错误信息）
- **流转**: 完成后自动进入 Stage 2

### Stage 2: PR Analysis Query
- **工具**: `github-cli` (gh)
- **命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **描述**: 使用 GitHub CLI 查询包含特定 Git SHA 的已合并 Pull Request。返回 PR 的编号、标题和 URL 的 JSON 数据。
- **输入**: 接受多种参数，包括仓库信息、搜索条件、输出格式等
- **输出**: 
  - JSON 格式的 PR 列表数据
  - 可选的压缩文件输出
  - HTTP 请求/响应详情
- **流转**: 完成后自动进入 Stage 3

### Stage 3: Command Link Creation
- **工具**: `browser` (npm)
- **命令**: `npm link`
- **描述**: 创建全局可用的命令链接，使项目中的工具可以在系统任何位置调用。
- **输入**: 无特定输入（继承上一阶段的上下文）
- **输出**: 链接创建结果状态字符串
- **流转**: 完成后自动进入 Stage 4

### Stage 4: Release Tag Fetching
- **工具**: `github-cli` (gh)
- **命令**: `gh release view --json tagName --jq '.tagName'`
- **描述**: 获取仓库最新发布的标签名称。使用 `jq` 从 JSON 响应中提取纯净的标签字符串。
- **输入**: 接受多种参数，包括仓库信息、输出格式、过滤选项等
- **输出**: 
  - 最新发布标签名称（字符串）
  - 可选的原始 JSON 响应
  - 压缩文件输出
- **流转**: 完成后自动进入 Stage 5

### Stage 5: Finalization & Iteration
- **工具**: `browser` (npm)
- **命令**: `npm install`
- **描述**: 再次安装依赖以确保环境一致性，并标记当前迭代周期完成。这是流水线的最后阶段，完成后会自动重启开始新一轮分析。
- **输入**: 无特定输入（继承所有先前阶段的上下文）
- **输出**: 最终安装结果状态字符串
- **流转**: 完成后自动重启到 Stage 1，开始下一轮迭代

## Data Flow

流水线的数据流转遵循以下模式：
```
[Stage 1] → (状态数据) → [Stage 2] → (JSON 数据) → [Stage 3] → 
(状态数据) → [Stage 4] → (标签数据) → [Stage 5] → (循环重启)
```

每个阶段的输出都会作为隐式上下文传递给下一阶段。关键数据（如查询到的 SHA、PR 列表、发布标签）会在整个流水线中保持可用。

## Configuration

流水线可以通过以下环境变量进行配置：

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `TARGET_SHA` | (自动检测) | 要搜索的 Git SHA 值 |
| `GITHUB_REPO` | (当前目录) | 目标 GitHub 仓库 |
| `OUTPUT_FORMAT` | `json` | 输出格式（json/text） |
| `ITERATION_DELAY` | `5` | 迭代之间的延迟秒数 |
| `STOP_AFTER_STAGE` | `5` | 调试用：在指定阶段后停止 |

## Notes

1. **认证要求**: Stage 2 和 Stage 4 需要有效的 GitHub CLI 认证 (`gh auth login`)
2. **网络连接**: 所有阶段都需要互联网连接来访问 npm 注册表和 GitHub API
3. **错误处理**: 任何阶段的失败都会导致整个流水线暂停，并在修复后从中断点继续
4. **迭代优化**: 每次完整运行后，流水线会分析性能指标并优化下一轮的参数

此工具仅用于合法的仓库分析和开发工作流程自动化。