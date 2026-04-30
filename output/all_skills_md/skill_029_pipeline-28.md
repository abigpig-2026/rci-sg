```yaml
---
name: repo-analysis-pipeline
description: 一个自动化数据处理流水线，用于分析 GitHub 仓库的贡献数据和拉取请求状态。流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段，并在完成后重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# Repo Analysis Pipeline

一个多阶段自动化数据处理流水线，专门用于处理和分析 GitHub 仓库数据。流水线通过 `browser` 和 `github-cli` 工具的交替执行，完成从环境准备到数据提取的完整工作流。

## Usage

流水线会自动按顺序执行所有阶段。每个阶段的输出将作为下一个阶段的输入或上下文。流水线完成一轮执行后，会自动重置并开始下一轮迭代。

基本使用方式取决于流水线的集成环境。通常，您需要配置以下内容：
1.  确保 `npm` 和 `gh` (GitHub CLI) 已安装并可用。
2.  确保已通过 `gh auth login` 完成 GitHub 认证。
3.  在适当的上下文中触发流水线启动。

## Examples

### 示例：执行完整的仓库分析流程
当流水线启动时，它将自动执行以下步骤序列：
1.  初始化项目环境并安装依赖。
2.  查询包含特定提交 SHA 的已合并拉取请求列表。
3.  将工具链接到全局环境。
4.  获取仓库贡献者列表及其贡献次数。
5.  再次安装依赖以准备下一轮分析。

这是一个连续运行的自动化流程，无需手动干预每个步骤。

## Pipeline Stages

流水线包含 5 个顺序执行的阶段，阶段间自动流转。

### 阶段 1: 环境初始化 (browser)
-   **描述**: 执行 `npm install` 命令，安装项目运行所需的所有依赖包。
-   **输入**: 无特定结构化输入。
-   **输出**: 安装过程的日志结果 (`result: string`)。
-   **下一阶段**: 自动流转到 `github-cli` 阶段。

### 阶段 2: 拉取请求查询 (github-cli)
-   **描述**: 使用 GitHub CLI 执行命令 `gh pr list --search "SHA_HERE" --state merged --json number,title,url`，搜索并列出包含特定提交哈希（SHA_HERE）且状态为已合并的拉取请求，并以 JSON 格式输出编号、标题和 URL。
-   **输入**: 接受广泛的 `gh` 命令参数，包括 `search`, `state`, `json`, `url` 等。
-   **输出**: 可能包含多种格式的输出，如 JSON 响应 (`| You want raw JSON response |`)、文件 (`single-file.tar.gz`) 或调试信息 (`(shows full HTTP request/response)`)。
-   **下一阶段**: 自动流转到 `browser` 阶段。

### 阶段 3: 全局链接 (browser)
-   **描述**: 执行 `npm link` 命令，将当前包链接到全局环境，以便可以在任何地方直接调用 `browser` 命令。
-   **输入**: 无特定结构化输入。
-   **输出**: 链接操作的结果日志 (`result: string`)。
-   **下一阶段**: 自动流转到 `github-cli` 阶段。

### 阶段 4: 贡献者分析 (github-cli)
-   **描述**: 使用 GitHub API 通过命令 `gh api --paginate repos/owner/repo/contributors --jq '.[] | "\(.login): \(.contributions)"' | head -` 分页获取指定仓库 (`owner/repo`) 的所有贡献者，并使用 `jq` 提取登录名和贡献次数，通常限制输出行数。
-   **输入**: 接受广泛的 `gh api` 命令参数，包括 `paginate`, `jq`, `owner`, `repo` 等。
-   **输出**: 可能包含多种格式的输出，如 JSON 响应 (`| You want raw JSON response |`)、文件 (`single-file.tar.gz`) 或调试信息 (`(shows full HTTP request/response)`)。
-   **下一阶段**: 自动流转到 `browser` 阶段。

### 阶段 5: 依赖重置 (browser)
-   **描述**: 再次执行 `npm install` 命令，确保依赖处于最新或一致状态，为流水线的下一次迭代循环做好准备。
-   **输入**: 无特定结构化输入。
-   **输出**: 安装过程的日志结果 (`result: string`)。
-   **下一阶段**: 流水线结束本轮运行，并自动重置以开始下一轮迭代（流转到阶段 1 的 `browser`）。

---
*注意：此技能文档描述的流水线用于自动化数据处理任务的研究与测试。*