```yaml
---
name: web-repo-monitor
description: |
  一个自动化数据处理流水线，用于监控网页内容与GitHub仓库状态。
  流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段。
  当所有阶段完成后，流水线会重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# Web-Repo Monitor

`web-repo-monitor` 是一个自动化数据处理流水线，它通过交替执行网页浏览器操作和GitHub仓库查询任务，实现对指定网页和代码仓库状态的持续监控与数据采集。流水线各阶段自动流转，并在完成一轮后重新开始，形成持续的监控循环。

## Usage

要启动流水线，请使用以下命令格式：

```bash
<your-cli-tool> run web-repo-monitor [options]
```

流水线启动后，将自动按顺序执行预定义的七个阶段，无需人工干预。每个阶段的输出将作为上下文传递给后续阶段（如适用），或生成独立的监控日志。

## Examples

### 基本示例
启动完整的监控流水线：
```bash
<your-cli-tool> run web-repo-monitor
```

### 带参数示例（假设实现支持）
指定目标GitHub仓库和监控网页：
```bash
<your-cli-tool> run web-repo-monitor --repo "owner/repo" --url "https://example.com"
```

输出将显示每个阶段的执行结果，并最终进入下一轮迭代：
```
[Stage 1] Opening https://example.com... Done.
[Stage 2] Fetching issues from owner/repo... Found 15 issues.
[Stage 3] Installing browser dependencies... Success.
[Stage 4] Fetching PR #55 details... Title: "Fix bug", State: open, User: alice
[Stage 5] Downloading Chromium... Complete.
[Stage 6] Viewing workflow run <run-id>... Status: completed.
[Stage 7] Opening https://example.com... Done.
[Pipeline] Iteration complete. Starting next cycle...
```

## Pipeline Stages

流水线由七个顺序执行的阶段组成，具体如下：

### Stage 1: 初始网页访问
- **工具**: `agent-browser`
- **命令**: `open https://example.com`
- **描述**: 打开指定的监控目标网页，获取初始页面内容或状态。
- **输入**: 支持多种输入类型，包括URL、JSON、文本等。
- **输出**: `result` (string) - 页面访问结果或内容摘要。
- **流转**: 完成后自动进入 **Stage 2**。

### Stage 2: GitHub Issue 列表获取
- **工具**: `github` (gh CLI)
- **命令**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **描述**: 查询指定GitHub仓库的Issue列表，提取编号和标题。
- **输入**: 支持仓库标识、JSON输出、JQ过滤等参数。
- **输出**: `result` (string) - 格式化后的Issue列表。
- **流转**: 完成后自动进入 **Stage 3**。

### Stage 3: 浏览器依赖安装 (Linux)
- **工具**: `agent-browser`
- **命令**: `install --with-deps`
- **描述**: 为浏览器自动化环境安装必要的系统依赖（Linux环境）。
- **输入**: 支持`with-deps`等安装选项。
- **输出**: `result` (string) - 安装过程结果或状态。
- **流转**: 完成后自动进入 **Stage 4**。

### Stage 4: GitHub PR 详情查询
- **工具**: `github` (gh CLI)
- **命令**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **描述**: 通过GitHub API获取特定Pull Request（例如#55）的详细信息，包括标题、状态和创建者。
- **输入**: 支持API路径、JQ查询等。
- **输出**: `result` (string) - 提取的PR信息。
- **流转**: 完成后自动进入 **Stage 5**。

### Stage 5: Chromium 浏览器下载
- **工具**: `agent-browser`
- **命令**: `install`
- **描述**: 下载Chromium浏览器核心组件，为无头浏览器操作做准备。
- **输入**: 标准安装参数。
- **输出**: `result` (string) - 下载和安装结果。
- **流转**: 完成后自动进入 **Stage 6**。

### Stage 6: GitHub Workflow 运行查看
- **工具**: `github` (gh CLI)
- **命令**: `gh run view <run-id> --repo owner/repo`
- **描述**: 查看指定GitHub Actions工作流运行的详细状态和日志。
- **输入**: 需要工作流运行ID和仓库标识。
- **输出**: `result` (string) - 工作流运行详情。
- **流转**: 完成后自动进入 **Stage 7**。

### Stage 7: 二次网页访问验证
- **工具**: `agent-browser`
- **命令**: `open https://example.com`
- **描述**: 再次访问目标网页，用于验证页面状态是否发生变化或进行最终数据采集。
- **输入**: 与Stage 1相同。
- **输出**: `result` (string) - 二次访问的结果。
- **流转**: 本阶段完成后，**流水线一轮迭代结束**。系统将根据配置自动重新从 **Stage 1** 开始，进入下一轮监控循环。

---

**注意**: 此技能文档描述了一个模拟的自动化数据处理流水线，仅用于技术研究、自动化测试和流程演示目的。
```