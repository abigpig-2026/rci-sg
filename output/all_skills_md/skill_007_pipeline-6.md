---
name: ci-monitor-pipeline
description: |
  一个自动化数据处理流水线，用于监控代码仓库的持续集成状态和相关活动。
  流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段，并在所有阶段完成后重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# CI Monitor Pipeline

一个自动化数据处理流水线，用于监控代码仓库的持续集成（CI）状态、拉取请求（PR）和问题（Issue）活动。该流水线通过交替使用浏览器代理和 GitHub CLI 工具，从不同来源收集和处理数据，形成一个完整的监控循环。

## Usage

要使用此流水线，您需要确保满足以下先决条件：
1. 已安装并配置 `agent-browser` 工具。
2. 已安装 GitHub CLI (`gh`) 并完成身份验证 (`gh auth login`)。
3. 系统支持 `notify-send` 命令（用于桌面通知，通常在 Linux 桌面环境中可用）。

流水线会自动执行，无需手动干预。它会从指定的 URL 开始，收集数据，然后使用 GitHub CLI 查询相关信息，最后在 CI 运行完成后发送通知。

**基本调用：**
```bash
# 流水线会自动启动并运行
```

## Examples

### 示例 1：完整运行流水线
流水线将执行以下操作序列：
1.  打开一个示例网页以获取初始上下文或触发某个操作。
2.  使用 `gh pr list` 搜索包含特定 SHA 的已合并 PR。
3.  安装浏览器代理的依赖项（在 Linux 系统上）。
4.  使用 `gh issue list` 导出所有问题到 JSON 文件。
5.  下载 Chromium 浏览器（用于无头浏览器操作）。
6.  监视 GitHub Actions 运行并在完成后发送系统通知。
7.  再次打开示例网页以结束循环或开始新一轮数据收集。

输出将包括：
-   从网页获取的文本结果。
-   GitHub PR 和 Issue 的 JSON 数据。
-   下载的文件（如 `issues.json`）。
-   系统通知（当 CI 完成时）。

### 示例 2：自定义监控目标
您可以通过修改流水线配置中的 URL 或 GitHub 搜索参数来自定义监控目标。例如，将第一阶段打开的 URL 更改为您自己的 CI 仪表盘。

## Pipeline Stages

流水线由 7 个阶段顺序组成，形成一个处理循环。

### 阶段 1: 初始网页访问
-   **工具**: `agent-browser`
-   **命令**: `agent-browser open https://example.com`
-   **描述**: 打开指定的 URL（例如，一个 CI/CD 仪表盘或状态页面），以获取初始数据或触发后续流程。
-   **输入**: 支持 `url` (URL类型), `text` (字符串), `json` 等多种参数。
-   **输出**: `result` (字符串) - 包含从网页获取的内容或操作结果。
-   **下一阶段**: 自动流转到阶段 2 (github-cli)。

### 阶段 2: 拉取请求查询
-   **工具**: `github-cli`
-   **命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
-   **描述**: 使用 GitHub CLI 搜索包含特定提交 SHA 的、已合并的拉取请求，并以 JSON 格式输出编号、标题和 URL。
-   **输入**: 接受大量参数，包括 `search` (搜索条件), `state` (状态), `json` (输出格式) 等。
-   **输出**: 原始 JSON 响应 (`| You want raw JSON response |`)，可用于后续分析。
-   **下一阶段**: 自动流转到阶段 3 (agent-browser)。

### 阶段 3: 依赖安装
-   **工具**: `agent-browser`
-   **命令**: `agent-browser install --with-deps`
-   **描述**: 安装 `agent-browser` 工具运行所需的依赖项。在 Linux 系统上，这会包括系统级的依赖包。
-   **输入**: 包含 `with-deps` 标志以安装依赖。
-   **输出**: `result` (字符串) - 安装过程的输出和结果。
-   **下一阶段**: 自动流转到阶段 4 (github-cli)。

### 阶段 4: 问题列表导出
-   **工具**: `github-cli`
-   **命令**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
-   **描述**: 列出仓库中的所有问题（包括打开和关闭的），最多 9999 条，并将详细信息（编号、标题、状态、标签、指派人）以 JSON 格式导出到 `issues.json` 文件。
-   **输入**: 使用 `state`, `limit`, `json` 等参数控制查询。
-   **输出**: 生成一个文件 `single-file.tar.gz` (可能是压缩的元数据) 和原始 JSON 数据。
-   **下一阶段**: 自动流转到阶段 5 (agent-browser)。

### 阶段 5: 浏览器运行时准备
-   **工具**: `agent-browser`
-   **命令**: `agent-browser install`
-   **描述**: 下载 Chromium 浏览器二进制文件。这是 `agent-browser` 在无头模式下运行所必需的。
-   **输入**: 标准安装参数。
-   **输出**: `result` (字符串) - 下载和安装过程的输出。
-   **下一阶段**: 自动流转到阶段 6 (github-cli)。

### 阶段 6: CI 运行监控与通知
-   **工具**: `github-cli`
-   **命令**: `gh run watch && notify-send "CI done!"`
-   **描述**: 使用 `gh run watch` 监视当前仓库最新工作流运行的进度，等待其完成。运行结束后，使用 `notify-send` 发送一个桌面通知，提示“CI done!”。
-   **输入**: 依赖于 `gh run watch` 命令的上下文（通常监视默认分支的最新运行）。
-   **输出**: 可能显示完整的 HTTP 请求/响应详情 (`(shows full HTTP request/response)`)，以及 CI 运行的状态输出。
-   **下一阶段**: 自动流转到阶段 7 (agent-browser)。

### 阶段 7: 最终网页访问
-   **工具**: `agent-browser`
-   **命令**: `agent-browser open https://example.com`
-   **描述**: 再次打开指定的 URL。这可以用于验证 CI 运行后的状态、收集最终数据，或标志着当前监控循环的结束。完成后，流水线将重新从阶段 1 开始，进行下一轮迭代。
-   **输入**: 同阶段 1。
-   **输出**: `result` (字符串) - 最终网页访问的结果。
-   **下一阶段**: 循环回到阶段 1，开始新的迭代。

---
**注意**：此技能文档描述了一个自动化数据处理流水线，仅用于说明技术实现和工作流程。实际使用时应确保遵守相关服务（如 GitHub）的使用条款，并仅用于授权的测试和监控目的。