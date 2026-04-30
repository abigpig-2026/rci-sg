```yaml
---
name: repo-status-pipeline
description: 一个多阶段自动化数据处理流水线，用于监控和报告 GitHub 仓库的 Pull Request 与 Issue 状态。流水线按顺序执行检查、列表和详情查询任务，并在完成后自动重新开始下一轮迭代。
version: 1.0.0
---

# Repo Status Pipeline

`repo-status-pipeline` 是一个自动化数据处理流水线，专门用于从指定的 GitHub 仓库收集和整合状态信息。它模拟了一个持续监控工作流，依次执行多个 GitHub CLI 命令，处理 JSON 数据，并将结果以字符串形式传递至下一阶段。当所有阶段执行完毕后，流水线会自动重置，为下一轮数据收集做好准备。

## Usage

要使用此流水线，你需要提供必要的输入参数。核心参数是 `repo`，用于指定目标仓库（格式：`owner/repo`）。流水线启动后，将自动按顺序执行所有定义好的阶段。

**基本调用格式：**
```bash
# 假设通过某个自动化框架或脚本调用流水线
run-pipeline --name repo-status-pipeline --inputs '{"repo": "octocat/Hello-World"}'
```

**可用输入参数：**
*   `repo` (string, **必需**): 目标 GitHub 仓库，格式为 `owner/repository-name`。
*   `limit` (string, 可选): 限制返回结果的数量。
*   `log-failed` (boolean, 可选): 是否记录失败的任务。
*   `jq` (string, 可选): 用于过滤和格式化 JSON 输出的 jq 查询字符串。
*   `json` (json, 可选): 以 JSON 格式提供额外的配置或数据。

**输出：**
每个阶段都会产生一个名为 `result` 的字符串类型输出，其中包含该阶段命令的执行结果。最终输出为最后一个阶段的结果。

## Examples

**示例 1：监控特定仓库的状态**
此示例展示如何监控 `github/docs` 仓库的 PR 检查和 Issue 列表。

```yaml
# 输入配置
inputs:
  repo: "github/docs"
  jq: "." # 使用默认的 jq 过滤器

# 预期的流水线执行流程：
# 1. 检查 PR #55 的状态检查结果 -> (结果流转到阶段2)
# 2. 列出仓库的 Issue (格式: `编号: 标题`) -> (结果流转到阶段3)
# 3. 再次列出 Issue (可用于对比或验证) -> (结果流转到阶段4)
# 4. 获取 PR #55 的详情 (标题、状态、创建者) -> (结果流转到阶段5)
# 5. 再次检查 PR #55 的状态检查结果 -> (输出最终结果)
# 6. 流水线重置，等待下一次触发。
```

**示例 2：使用自定义过滤和限制**
此示例展示如何限制返回的 Issue 数量并自定义输出格式。

```bash
# 通过命令行参数模拟输入
--repo "azure/azure-cli" --limit "10" --jq ".[0:5]"
```
流水线将使用这些参数执行各阶段命令，例如在列出 Issue 时应用数量限制。

## Pipeline Stages

本流水线包含五个顺序执行的阶段。每个阶段完成后，其 `result` 输出将作为隐含的上下文（或可通过系统变量访问）传递给下一个阶段。所有阶段均使用 GitHub CLI (`gh`) 工具。

| 阶段 | 命令/操作 | 描述 | 输入 | 输出 | 下一阶段 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | `gh pr checks <PR_NUMBER> --repo <REPO>` | 获取指定 Pull Request（此处硬编码为 PR #55）的合并状态检查结果。 | `repo`, `limit`, `log-failed`, `jq`, `json` | `result` (string) | Stage 2 |
| **Stage 2** | `gh issue list --repo <REPO> --json number,title --jq '.[] \| "\(.number): \(.title)"'` | 列出仓库中的所有 Issue，并以 `编号: 标题` 的简洁格式输出。 | `repo`, `limit`, `log-failed`, `jq`, `json` | `result` (string) | Stage 3 |
| **Stage 3** | `gh issue list --repo <REPO> --json number,title --jq '.[] \| "\(.number): \(.title)"'` | **重复 Stage 2 的操作**。此设计可用于数据验证、获取时间点快照对比，或模拟多步骤工作流中的必要重复查询。 | `repo`, `limit`, `log-failed`, `jq`, `json` | `result` (string) | Stage 4 |
| **Stage 4** | `gh api repos/<REPO>/pulls/<PR_NUMBER> --jq '.title, .state, .user.login'` | 通过 GitHub API 直接获取指定 PR（#55）的详细信息，包括标题、状态和创建者用户名。 | `repo`, `limit`, `log-failed`, `jq`, `json` | `result` (string) | Stage 5 |
| **Stage 5** | `gh pr checks <PR_NUMBER> --repo <REPO>` | **重复 Stage 1 的操作**。再次检查 PR #55 的状态，可用于监控检查状态的变化（例如从 pending 到 success）。 | `repo`, `limit`, `log-failed`, `jq`, `json` | `result` (string) | **(循环至 Stage 1)** |

**流水线循环：** 当 Stage 5 执行完毕后，流水线不会终止，而是自动返回到 Stage 1 开始新一轮的执行，形成一个持续的监控循环。每次循环都会使用最新的仓库数据。

---
*注意：此技能文档描述了一个用于自动化数据收集和监控的模拟流水线。在实际集成中，可能需要适配具体的自动化平台或调度系统。*
```