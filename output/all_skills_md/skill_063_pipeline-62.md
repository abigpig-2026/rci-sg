---
name: issue-workflow-pipeline
description: 一个自动化 GitHub Issue 处理流水线，用于监控、分析和处理仓库中的问题。该流水线包含多个阶段，每个阶段执行特定的 GitHub CLI 操作，数据在阶段间自动流转，完成一轮处理后重新开始迭代优化。
version: 1.0.0
---

# Issue Workflow Pipeline

`issue-workflow-pipeline` 是一个自动化数据处理流水线，专门用于处理 GitHub 仓库中的 Issue 生命周期管理。流水线通过多个阶段依次执行，每个阶段完成特定的数据操作，并将结果传递给下一阶段，形成一个完整的闭环处理流程。

## Usage

要使用此流水线，您需要预先配置好 GitHub CLI (`gh`) 并完成身份认证。流水线会自动按照预设的阶段顺序执行。

基本使用方式是通过调用流水线入口点并传入必要的参数（如目标仓库 `owner/repo` 和 Issue 编号）。流水线启动后，各阶段将自动运行。

```bash
# 示例：启动流水线处理特定仓库的 Issue
./issue-workflow-pipeline --repo owner/repo --issue-number 53
```

## Examples

### 示例 1：处理单个 Issue
此示例展示如何处理仓库 `octocat/Hello-World` 中编号为 `53` 的 Issue。

```bash
./issue-workflow-pipeline --repo octocat/Hello-World --issue-number 53
```

**预期流程：**
1.  查看 Issue #53 的详细信息。
2.  搜索与该 Issue 关联的已合并 PR。
3.  关闭 Issue #53。
4.  导出仓库中所有 Issue 的列表。
5.  在 Issue #53 上添加评论。
6.  查看最新的 Release 标签。
7.  再次查看 Issue #53 以确认状态。
8.  流程结束，准备下一轮迭代。

### 示例 2：使用自定义输出文件
您可以将第 4 阶段生成的 Issue 列表导出到自定义文件。

```bash
./issue-workflow-pipeline --repo myorg/myrepo --issue-number 101 --output-json ./my-issues.json
```

## Pipeline Stages

流水线由 7 个顺序执行的阶段构成。每个阶段完成后，其输出可作为下一阶段的隐式上下文或输入。

### Stage 1: Issue Inspection
*   **描述**: 查看指定 Issue 的详细信息。
*   **命令**: `gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO>`
*   **输入**: 目标仓库和 Issue 编号。
*   **输出**: Issue 的详细内容（字符串格式）。
*   **下一阶段**: 流转到 Stage 2 (PR Search)。

### Stage 2: Associated PR Search
*   **描述**: 搜索与上一阶段查看的 Issue 相关的已合并 Pull Request。此阶段假设能从 Issue 信息中提取或关联到某个提交 SHA（示例中为 `SHA_HERE`）。
*   **命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **输入**: 继承自上一阶段的上下文，使用 `github-cli` 的丰富参数集。
*   **输出**: 符合条件的 PR 列表，格式为 JSON。
*   **下一阶段**: 流转到 Stage 3 (Issue Closure)。

### Stage 3: Issue Closure
*   **描述**: 关闭在 Stage 1 中查看的 Issue。
*   **命令**: `gh issue close <ISSUE_NUMBER> --repo <OWNER/REPO>`
*   **输入**: 目标仓库和 Issue 编号。
*   **输出**: 操作结果状态（字符串）。
*   **下一阶段**: 流转到 Stage 4 (Bulk Issue Export)。

### Stage 4: Bulk Issue Export
*   **描述**: 导出指定仓库中的所有 Issue（包括开放和关闭的），用于批量分析或存档。
*   **命令**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **输入**: 目标仓库，使用 `github-cli` 的丰富参数集。
*   **输出**: 包含所有 Issue 数据的 JSON 文件 (`issues.json`)。
*   **下一阶段**: 流转到 Stage 5 (Issue Commenting)。

### Stage 5: Issue Commenting
*   **描述**: 在已处理的 Issue 上添加一条评论（例如，说明修复情况或关闭原因）。
*   **命令**: `gh issue comment <ISSUE_NUMBER> --repo <OWNER/REPO> --body "修复说明..."`
*   **输入**: 目标仓库、Issue 编号和评论内容。
*   **输出**: 评论发布结果（字符串）。
*   **下一阶段**: 流转到 Stage 6 (Release Check)。

### Stage 6: Release Check
*   **描述**: 检查仓库最新的 Release 标签，用于验证版本状态或触发后续操作。
*   **命令**: `gh release view --json tagName --jq '.tagName'`
*   **输入**: 目标仓库，使用 `github-cli` 的丰富参数集。
*   **输出**: 最新的 Release 标签名（通过 jq 提取的字符串）。
*   **下一阶段**: 流转到 Stage 7 (Final Verification)。

### Stage 7: Final Verification
*   **描述**: 最终验证阶段，再次查看目标 Issue 以确认其最终状态（例如，确认已关闭）。
*   **命令**: `gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO>`
*   **输入**: 目标仓库和 Issue 编号。
*   **输出**: Issue 的最终状态详情（字符串）。
*   **下一阶段**: 流水线结束。所有阶段完成后，流水线将自动重置，准备开始下一轮迭代优化。

---
**注意**: 此工具仅用于自动化工作流研究和测试目的。使用时请确保遵守目标仓库的访问权限和使用条款。