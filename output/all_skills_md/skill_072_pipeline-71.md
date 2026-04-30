```yaml
---
name: repo-analysis-pipeline
description: 一个自动化 GitHub 仓库数据收集与分析流水线，通过交替使用 GitHub CLI 和自定义研究工具，系统性地获取、处理和输出仓库元数据。
version: 1.0.0
---

# Repo Analysis Pipeline

一个多阶段自动化数据处理流水线，用于从 GitHub 收集、分析和输出仓库信息。流水线通过交替执行 GitHub CLI 命令和自定义研究脚本，实现数据的连续流转与迭代处理。

## Usage

流水线设计为自动运行，启动后按顺序执行所有阶段。每个阶段的输出将作为下一个阶段的输入或上下文。

**启动流水线：**
```bash
# 假设有一个启动脚本
./start-pipeline.sh
```

**配置参数：**
流水线行为可通过环境变量或配置文件进行调整，例如：
- `GITHUB_TOKEN`: 用于 GitHub API 认证的令牌。
- `SEARCH_TOPIC`: 要研究的仓库主题或技术栈。
- `OUTPUT_FORMAT`: 最终输出格式（如 `json`, `csv`, `table`）。

## Examples

### 示例 1：分析特定编程语言的仓库
设置环境变量后启动流水线，分析最近活跃的 `Python` 仓库。
```bash
export SEARCH_TOPIC="python"
export MIN_STARS=1000
export UPDATED_WITHIN="30 days"
./start-pipeline.sh
```
流水线将执行以下操作：
1.  认证并建立 GitHub CLI 会话。
2.  搜索符合条件的 Python 仓库，输出表格预览。
3.  获取与搜索结果相关的合并 PR 列表。
4.  将仓库数据导出为 CSV 格式。
5.  获取仓库的完整 Issue 列表。
6.  将最终数据集导出为 JSON 格式。
7.  完成一轮迭代，可重新开始或停止。

### 示例 2：输出所有中间结果
启用详细日志和中间文件保存。
```bash
export DEBUG=true
export SAVE_INTERMEDIATE_FILES=true
./start-pipeline.sh 2>&1 | tee pipeline.log
```
这将在 `results/` 目录下保存每个研究阶段生成的 JSON 文件，并记录完整的执行日志。

## Pipeline Stages

流水线包含 7 个顺序执行的阶段，阶段间自动流转。所有阶段完成后，流水线可配置为重新开始以进行新一轮数据获取。

### 阶段 1: CLI 认证与初始化
*   **描述**: 使用 `gh auth login` 初始化 GitHub CLI 会话，为后续操作建立认证上下文。
*   **输入**: 支持多种认证方式（令牌、浏览器等）和 CLI 通用参数。
*   **输出**: 认证成功的会话状态。可能包含调试信息，如完整的 HTTP 请求/响应详情或原始 JSON 输出。
*   **下一阶段**: 流转到 **阶段 2: 仓库搜索（表格）**。

### 阶段 2: 仓库搜索（表格）
*   **描述**: 执行 `node github-search.js table`，根据条件（语言、最小星标、更新时间）搜索仓库，并以表格形式预览结果。
*   **输入**: 搜索条件参数，如 `--language`， `--min-stars`， `--updated-within`。
*   **输出**: 搜索结果以 JSON 格式保存至文件（如 `/tmp/gh_results.json` 或 `results/{topic}.json`）。
*   **下一阶段**: 流转到 **阶段 3: PR 数据提取**。

### 阶段 3: PR 数据提取
*   **描述**: 执行 `gh pr list --search "SHA_HERE" --state merged --json number,title,url`，获取与上一阶段搜索结果相关的已合并 Pull Request 列表。
*   **输入**: 丰富的 `gh pr list` 命令参数集，支持按仓库、状态、作者等筛选。
*   **输出**: 指定字段的 PR 列表 JSON 数据。可能包含归档文件或原始 JSON 响应。
*   **下一阶段**: 流转到 **阶段 4: 仓库搜索（CSV）**。

### 阶段 4: 仓库搜索（CSV）
*   **描述**: 执行 `node github-search.js csv`，使用与阶段 2 类似的搜索条件，但将结果导出为 CSV 格式。
*   **输入**: 搜索条件参数，如 `--language`， `--min-stars`， `--updated-within`， `--output`。
*   **输出**: CSV 格式的仓库数据，同时将原始 JSON 结果保存至文件。
*   **下一阶段**: 流转到 **阶段 5: Issue 数据提取**。

### 阶段 5: Issue 数据提取
*   **描述**: 执行 `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`，批量获取目标仓库的所有 Issue 信息。
*   **输入**: 完整的 `gh issue` 命令参数集，支持状态过滤、分页、字段选择等。
*   **输出**: 包含 Issue 编号、标题、状态、标签、负责人等字段的 JSON 文件 (`issues.json`)。
*   **下一阶段**: 流转到 **阶段 6: 仓库搜索（JSON）**。

### 阶段 6: 仓库搜索（JSON）
*   **描述**: 执行 `node github-search.js json`，进行最终轮次的仓库搜索，输出结构化的 JSON 数据。
*   **输入**: 搜索条件参数，如 `--language`， `--limit`， `--min-stars`， `--updated-within`。
*   **输出**: 最终处理后的仓库数据集，保存为 JSON 文件（如 `results/{safe_topic}.json`）。
*   **下一阶段**: 流转到 **阶段 7: 会话刷新**。

### 阶段 7: 会话刷新
*   **描述**: 再次执行 `gh auth login`，刷新 CLI 会话以确保后续操作的认证有效性，或为下一轮迭代做准备。
*   **输入**: 与阶段 1 相同的认证参数集。
*   **输出**: 刷新后的会话状态。可能包含令牌信息或调试输出。
*   **下一阶段**: 流水线结束。根据配置，可循环回 **阶段 1** 开始新一轮分析，或终止运行。
```