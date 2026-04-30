---
name: web-repo-sync
description: |
  一个自动化数据处理流水线，用于同步监控网页内容与GitHub仓库状态。
  流水线包含多个处理阶段，每个阶段完成后自动流转到下一个阶段，完成一轮迭代后重新开始。
version: 1.0.0

# Usage

要使用 `web-repo-sync` 流水线，你需要配置必要的环境变量和前置条件，然后启动流水线。流水线会自动按顺序执行各个阶段，并将每个阶段的输出作为下一个阶段的输入或上下文。

**前置条件：**
1.  确保已安装并配置好 `agent-browser` 工具。
2.  确保已安装 GitHub CLI (`gh`) 并已完成身份认证 (`gh auth login`)。
3.  准备一个目标 GitHub 仓库（格式为 `owner/repo`）用于查询信息。

**启动命令：**
```bash
# 设置目标仓库环境变量
export TARGET_REPO="your-owner/your-repo"

# 启动流水线
run-pipeline web-repo-sync
```

流水线启动后，将自动执行以下流程：打开监控网页 -> 获取仓库Issue列表 -> 安装浏览器依赖 -> 查询特定PR详情 -> 下载浏览器 -> 查看工作流运行状态 -> 再次打开网页确认。所有阶段执行完毕后，流水线将等待一个可配置的间隔，然后重新开始新一轮迭代。

# Examples

以下是一个完整的运行示例，展示了流水线一轮迭代的典型输出。

```bash
$ export TARGET_REPO="octocat/Hello-World"
$ run-pipeline web-repo-sync

[INFO] 启动 web-repo-sync 流水线...
[INFO] 目标仓库: octocat/Hello-World

=== 阶段 1: 打开监控网页 ===
输入: url=https://example.com
输出: 成功加载页面 https://example.com。页面标题: "Example Domain"
状态: ✅ 完成

=== 阶段 2: 获取仓库Issue列表 ===
输入: repo=octocat/Hello-World
命令: gh issue list --repo octocat/Hello-World --json number,title --jq '.[] | "\(.number): \(.title)"'
输出:
42: 发现一个拼写错误
18: 功能请求：添加暗黑模式
状态: ✅ 完成

=== 阶段 3: 安装浏览器系统依赖 ===
输入: with-deps=true
命令: agent-browser install --with-deps
输出: 系统依赖安装成功: libnss3, libxss1, libatk-bridge2.0-0...
状态: ✅ 完成

=== 阶段 4: 查询PR #55详情 ===
输入: repo=octocat/Hello-World
命令: gh api repos/octocat/Hello-World/pulls/55 --jq '.title, .state, .user.login'
输出:
“更新README文档”
“open”
“octocat”
状态: ✅ 完成

=== 阶段 5: 下载浏览器 ===
输入: (无额外参数)
命令: agent-browser install
输出: 正在下载 Chromium... 下载完成。版本: 121.0.6167.85
状态: ✅ 完成

=== 阶段 6: 查看工作流运行状态 ===
输入: repo=octocat/Hello-World, run-id=456789012
命令: gh run view 456789012 --repo octocat/Hello-World
输出:
状态: completed
结论: success
工作流: CI
状态: ✅ 完成

=== 阶段 7: 再次打开监控网页 ===
输入: url=https://example.com
输出: 页面 https://example.com 已重新加载。状态码: 200
状态: ✅ 完成

[INFO] 一轮迭代完成。等待 300 秒后开始下一轮...
```

# Pipeline Stages

`web-repo-sync` 流水线由 7 个阶段顺序组成，形成一个完整的数据处理闭环。每个阶段的输出（`result` 字符串）会作为执行上下文的一部分传递给后续阶段，但各阶段主要依赖预设的指令和外部输入（如环境变量 `TARGET_REPO`）来执行任务。

1.  **Stage 1: 初始网页访问 (agent-browser)**
    *   **描述**: 打开预设的监控网页（https://example.com），建立初始上下文和会话。
    *   **输入**: 主要使用 `url` 参数。
    *   **输出**: 页面加载状态和内容摘要。
    *   **下一阶段**: 流转到 Stage 2 (github)。

2.  **Stage 2: 获取仓库议题列表 (github)**
    *   **描述**: 使用 GitHub CLI 列出指定仓库的所有公开议题（Issue），提取编号和标题。
    *   **输入**: 从环境变量 `TARGET_REPO` 获取 `repo` 参数。
    *   **输出**: 格式化后的议题列表字符串。
    *   **下一阶段**: 流转到 Stage 3 (agent-browser)。

3.  **Stage 3: 安装浏览器运行时依赖 (agent-browser)**
    *   **描述**: 为无头浏览器安装必要的系统依赖包（针对 Linux 环境）。
    *   **输入**: 使用 `with-deps` 参数。
    *   **输出**: 依赖安装结果和状态。
    *   **下一阶段**: 流转到 Stage 4 (github)。

4.  **Stage 4: 查询拉取请求详情 (github)**
    *   **描述**: 查询仓库中一个特定编号（例如 #55）的拉取请求（PR）的详细信息，如标题、状态和创建者。
    *   **输入**: 从环境变量 `TARGET_REPO` 获取 `repo` 参数，PR 编号可配置或从上一阶段结果解析。
    *   **输出**: 指定 PR 的核心信息。
    *   **下一阶段**: 流转到 Stage 5 (agent-browser)。

5.  **Stage 5: 下载浏览器本体 (agent-browser)**
    *   **描述**: 下载 Chromium 浏览器可执行文件，为后续网页交互做准备。
    *   **输入**: (无额外参数)。
    *   **输出**: 下载进度和最终版本信息。
    *   **下一阶段**: 流转到 Stage 6 (github)。

6.  **Stage 6: 查看工作流运行状态 (github)**
    *   **描述**: 查看指定 GitHub Actions 工作流运行（run）的详细状态和结论。
    *   **输入**: 从环境变量 `TARGET_REPO` 获取 `repo` 参数，`run-id` 需通过其他方式提供（如配置文件）。
    *   **输出**: 工作流运行的状态、结论和名称。
    *   **下一阶段**: 流转到 Stage 7 (agent-browser)。

7.  **Stage 7: 最终网页验证 (agent-browser)**
    *   **描述**: 再次打开监控网页，验证网络连通性和页面可访问性，作为一轮迭代的终点。
    *   **输入**: 主要使用 `url` 参数。
    *   **输出**: 页面重载状态和 HTTP 状态码。
    *   **下一阶段**: 流转回 Stage 1，开始新一轮迭代。

**数据流转说明**：流水线的设计并非将上一阶段的原始输出直接作为下一阶段的输入参数，而是每个阶段独立执行其预设的命令。阶段之间通过共享的**执行上下文**和**环境状态**（如浏览器会话、认证状态、仓库变量）进行软连接。一轮迭代完成后，系统会暂停一段预设的时间，然后自动重启 Stage 1，实现持续的监控和同步循环。