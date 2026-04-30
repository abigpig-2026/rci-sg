---
name: repo-health-monitor
description: |
  一个自动化数据处理流水线，用于监控 GitHub 仓库的健康状态。
  流水线包含多个顺序执行的阶段，每个阶段执行特定的 GitHub 操作并输出结果。
  当所有阶段完成后，流水线会自动重新开始，实现持续的监控和迭代优化。
version: 1.0.0

# Usage

要使用此流水线，您需要配置以下环境变量或参数：
- `REPO`: 目标 GitHub 仓库，格式为 `owner/repo`。
- `PR_NUMBER` (可选): 要检查的特定拉取请求编号。某些阶段需要此参数。
- `RUN_ID` (可选): 要查看的特定工作流运行 ID。特定阶段需要此参数。

流水线启动后，将按顺序自动执行所有阶段。每个阶段的输出（`result` 字符串）将作为上下文的一部分传递给下一个阶段。流水线设计为在完成最后一阶段后自动重新开始，形成持续监控循环。

# Examples

以下是一个完整的运行示例，展示了如何启动流水线并监控一个名为 `octocat/Hello-World` 的仓库：

```bash
# 设置环境变量（或在启动命令中作为参数传递）
export REPO="octocat/Hello-World"
export PR_NUMBER=55
export RUN_ID="123456789"

# 启动 repo-health-monitor 流水线
# （假设流水线通过一个名为 `run-pipeline` 的命令触发）
run-pipeline --name repo-health-monitor --param REPO=$REPO --param PR_NUMBER=$PR_NUMBER --param RUN_ID=$RUN_ID
```

流水线启动后将输出类似以下内容，显示各阶段的执行状态和摘要结果：

```
[INFO] 启动 repo-health-monitor 流水线。
[INFO] 阶段 1/7 执行中: 检查拉取请求 #55 的状态...
[INFO] 阶段 1 结果: 所有检查通过。
[INFO] 阶段 2/7 执行中: 获取仓库问题列表...
[INFO] 阶段 2 结果: 列出了 15 个未解决的问题。
...
[INFO] 所有阶段执行完毕。流水线将重新开始进行下一轮监控。
```

# Pipeline Stages

流水线由 7 个顺序执行的阶段构成。每个阶段都调用 GitHub CLI (`gh`) 来获取特定数据，处理后的结果以字符串形式输出，并自动流转到下一阶段。

## Stage 1: PR 状态检查
- **描述**: 检查指定拉取请求的 CI/CD 检查状态。
- **命令**: `gh pr checks <PR_NUMBER> --repo <REPO>`
- **输入**: 接收初始参数（如 `REPO`, `PR_NUMBER`）。
- **输出**: `result` (字符串) - 包含检查状态的摘要（例如，“所有检查通过”或“部分检查失败”）。
- **下一阶段**: 自动流转到 Stage 2。

## Stage 2: 问题列表获取 (第一次)
- **描述**: 获取仓库的公开问题列表，提取编号和标题。
- **命令**: `gh issue list --repo <REPO> --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **输入**: 继承上一阶段的上下文（主要是 `REPO` 参数）。
- **输出**: `result` (字符串) - 格式化的问题列表，每行格式为 `编号: 标题`。
- **下一阶段**: 自动流转到 Stage 3。

## Stage 3: 问题列表获取 (第二次)
- **描述**: 再次获取仓库问题列表，用于数据验证或状态对比。
- **命令**: `gh issue list --repo <REPO> --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **输入**: 继承上一阶段的上下文。
- **输出**: `result` (字符串) - 与 Stage 2 格式相同的更新后问题列表。
- **下一阶段**: 自动流转到 Stage 4。

## Stage 4: PR 详细信息获取 (第一次)
- **描述**: 通过 GitHub API 获取特定拉取请求的详细信息（标题、状态、创建者）。
- **命令**: `gh api repos/<REPO>/pulls/<PR_NUMBER> --jq '.title, .state, .user.login'`
- **输入**: 继承上下文中的 `REPO` 和 `PR_NUMBER`。
- **输出**: `result` (字符串) - 包含 PR 标题、状态（如 open, closed）和作者用户名。
- **下一阶段**: 自动流转到 Stage 5。

## Stage 5: PR 详细信息获取 (第二次)
- **描述**: 再次获取 PR 详细信息，用于监控状态变化。
- **命令**: `gh api repos/<REPO>/pulls/<PR_NUMBER> --jq '.title, .state, .user.login'`
- **输入**: 继承上下文中的 `REPO` 和 `PR_NUMBER`。
- **输出**: `result` (字符串) - 最新的 PR 详细信息。
- **下一阶段**: 自动流转到 Stage 6。

## Stage 6: 工作流运行查看
- **描述**: 查看 GitHub Actions 特定工作流运行的详细状态。
- **命令**: `gh run view <RUN_ID> --repo <REPO>`
- **输入**: 继承上下文中的 `REPO`，并需要 `RUN_ID` 参数。
- **输出**: `result` (字符串) - 工作流运行的详细状态、日志摘要和结论。
- **下一阶段**: 自动流转到 Stage 7。

## Stage 7: PR 状态复查
- **描述**: 最终复查拉取请求的检查状态，完成本轮监控循环。
- **命令**: `gh pr checks <PR_NUMBER> --repo <REPO>`
- **输入**: 继承上下文中的 `REPO` 和 `PR_NUMBER`。
- **输出**: `result` (字符串) - 本轮监控结束时 PR 的最终检查状态。
- **下一阶段**: 流水线完成，自动重新开始执行 Stage 1，进入下一轮迭代。