---
name: ci-monitor-pipeline
description: |
  一个自动化数据处理流水线，用于监控持续集成（CI）流程和相关的代码仓库活动。
  该流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段。
  当所有阶段完成后，流水线会重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# CI Monitor Pipeline

## Usage

要使用此流水线，请确保您的环境已安装并配置好以下工具：
- `agent-browser`：用于自动化浏览器操作和数据提取。
- `gh` (GitHub CLI)：用于与 GitHub API 交互。

流水线会自动按顺序执行所有阶段。您可以通过设置环境变量或提供初始输入参数来启动流水线。

**启动流水线：**
```bash
# 假设流水线由某个调度器或主控脚本调用
./run-pipeline.sh
```

## Examples

### 基本示例
此示例展示了流水线的一次完整执行周期，模拟监控一个 CI 流程。

```bash
# 流水线启动后，将自动执行以下阶段序列：
# 1. 打开监控仪表板网页
# 2. 查询与特定提交 SHA 相关的已合并 PR
# 3. 安装必要的系统依赖
# 4. 导出所有 Issue 状态到文件
# 5. 下载浏览器运行环境
# 6. 监控 CI 运行状态并发送通知
# 7. 再次打开仪表板确认结果
```

### 带自定义参数的示例
您可以通过环境变量调整流水线的行为，例如指定不同的仓库或搜索条件。

```bash
export GITHUB_REPO="owner/repo"
export TARGET_SHA="abc123def456"
export MONITOR_URL="https://internal-ci.example.com"
./run-pipeline.sh
```

## Pipeline Stages

本流水线由 7 个阶段顺序组成，形成一个闭环的数据处理流程。

### Stage 1: 初始监控页面加载
- **工具**: `agent-browser`
- **命令**: `agent-browser open https://example.com`
- **描述**: 打开预设的 CI/CD 或项目监控仪表板 URL，以获取初始状态和上下文信息。
- **输入**: 主要接受一个 URL 参数。
- **输出**: 返回页面加载结果（字符串格式），包含页面状态或提取的初始数据。
- **流转**: 输出作为上下文传递给下一阶段。

### Stage 2: 查询合并的 Pull Requests
- **工具**: `github-cli`
- **命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **描述**: 使用 GitHub CLI 查询与上一阶段可能提取的特定提交 SHA（占位符）相关的、已合并的 Pull Requests 列表，并以 JSON 格式输出关键信息。
- **输入**: 接受广泛的 `gh` 命令参数，包括 `--search`, `--state`, `--json` 等。期望从上一阶段获得 `SHA_HERE` 的具体值。
- **输出**: 生成包含 PR 编号、标题和 URL 的 JSON 数据。也可能输出调试文件或原始 HTTP 信息。
- **流转**: JSON 数据被传递到下一阶段进行进一步处理。

### Stage 3: 安装系统依赖
- **工具**: `agent-browser`
- **命令**: `agent-browser install --with-deps`
- **描述**: 为后续的浏览器自动化操作安装必要的运行时依赖项（例如在 Linux 系统上安装系统库）。
- **输入**: 接受 `--with-deps` 等参数，指示安装依赖。
- **输出**: 返回安装过程的结果状态（字符串）。
- **流转**: 安装成功状态作为上下文传递给下一阶段。

### Stage 4: 导出仓库 Issues 状态
- **工具**: `github-cli`
- **命令**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **描述**: 列出指定仓库的所有 Issues（包括打开和关闭状态），并将详细的 JSON 数据导出到本地文件 `issues.json`，用于存档或分析。
- **输入**: 接受 `--state`, `--limit`, `--json` 等参数，通常针对在 Stage 2 确定的仓库上下文。
- **输出**: 将 JSON 数据流重定向到文件 `issues.json`。同时可能输出辅助信息。
- **流转**: 生成的文件路径或数据摘要传递给下一阶段。

### Stage 5: 下载浏览器运行时
- **工具**: `agent-browser`
- **命令**: `agent-browser install`
- **描述**: 下载并安装无头浏览器（如 Chromium）的可执行文件，为深度网页交互做准备。
- **输入**: 标准安装命令参数。
- **输出**: 返回下载和安装结果（字符串）。
- **流转**: 浏览器就绪状态传递给下一阶段。

### Stage 6: 监控 CI 运行并通知
- **工具**: `github-cli`
- **命令**: `gh run watch && notify-send "CI done!"`
- **描述**: 监视当前仓库最新工作流运行的进度，等待其完成，然后使用桌面通知系统发送完成提示。
- **输入**: 接受 `gh run watch` 相关参数。依赖于前序阶段设置的仓库上下文。
- **输出**: 监控日志，并在完成后触发系统通知。
- **流转**: 监控完成事件作为触发器传递给最终阶段。

### Stage 7: 最终结果确认
- **工具**: `agent-browser`
- **命令**: `agent-browser open https://example.com`
- **描述**: 再次打开监控仪表板或 CI 结果详情页面，供用户或后续流程确认本轮监控的最终状态。
- **输入**: 可能使用与 Stage 1 相同或更新的 URL。
- **输出**: 返回最终页面的加载结果（字符串）。
- **流转**: 流水线完成一次迭代。输出可用于生成报告，随后流水线可根据配置暂停或重新开始新一轮迭代。

---
*注意：此技能文档描述的流水线仅用于自动化工作流研究和测试目的。*