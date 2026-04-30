```yaml
---
name: repo-release-analyzer
description: 一个自动化数据处理流水线，用于分析 GitHub 仓库的发布和合并请求数据。该流水线通过多个阶段处理数据，每个阶段完成后自动流转到下一阶段，并在完成所有阶段后重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# Repo Release Analyzer

`repo-release-analyzer` 是一个自动化数据处理流水线，专门用于处理和分析 GitHub 仓库的发布与合并请求（Pull Request）数据。流水线通过五个顺序执行的阶段，模拟了从环境准备到数据查询、再到结果处理的完整工作流。每个阶段处理完成后，数据会自动流转到下一阶段，形成一个闭环的自动化处理循环。

## Usage

要使用此流水线，您需要确保环境中已安装以下工具：
- **Node.js** 和 **npm**（用于执行 `browser` 阶段命令）
- **GitHub CLI (`gh`)**（用于执行 `github-cli` 阶段命令）

流水线会自动按顺序执行所有阶段。您可以通过配置环境变量（如 `GITHUB_TOKEN`）来授权 GitHub CLI 的访问。

基本使用流程是启动流水线，它将自动运行并输出各阶段的结果。

## Examples

以下是一个完整的流水线运行示例，展示了从开始到结束的数据流转过程：

```bash
# 假设流水线在一个包含 package.json 的 Node.js 项目目录中启动
# 阶段 1: 安装项目依赖
$ npm install
> 输出: "added 152 packages in 5s"

# 阶段 2: 查询包含特定提交 SHA 的已合并 PR 列表
# 假设 SHA_HERE 是一个环境变量或上一步的输出
$ gh pr list --search "a1b2c3d" --state merged --json number,title,url
> 输出: [{"number": 42, "title": "Fix bug", "url": "https://github.com/owner/repo/pull/42"}]

# 阶段 3: 将项目链接到全局命令
$ npm link
> 输出: "linked /path/to/project"

# 阶段 4: 查看最新发布的标签名
$ gh release view --json tagName --jq '.tagName'
> 输出: "v1.2.3"

# 阶段 5: 再次安装依赖（模拟迭代优化后的环境重置）
$ npm install
> 输出: "already up-to-date"

# 所有阶段完成，流水线将重新开始（阶段1），进行下一轮迭代。
```

## Pipeline Stages

流水线包含五个顺序执行的阶段，具体描述如下：

### Stage 1: Environment Setup (browser)
- **描述**: 执行 `npm install` 命令，安装项目所需的依赖包。这是流水线的初始化阶段，为后续的数据处理准备运行环境。
- **输入**: 无特定结构化输入。
- **输出**: 一个字符串类型的 `result`，包含安装过程的摘要信息（例如，添加的包数量、耗时）。
- **下一阶段**: 自动流转到 Stage 2 (github-cli)。

### Stage 2: PR Analysis (github-cli)
- **描述**: 执行 `gh pr list --search "SHA_HERE" --state merged --json number,title,url` 命令。此阶段根据一个特定的提交 SHA 值，查询 GitHub 仓库中所有已合并的 Pull Request，并以 JSON 格式返回 PR 编号、标题和 URL 信息。
- **输入**: 接受广泛的 GitHub CLI 命令参数，核心参数是 `--search`（用于指定提交 SHA）、`--state merged` 和 `--json`。
- **输出**: 主要输出为 JSON 格式的 PR 列表数据。也可能输出其他辅助信息，如文件或调试 URL。
- **下一阶段**: 自动流转到 Stage 3 (browser)。

### Stage 3: Command Registration (browser)
- **描述**: 执行 `npm link` 命令。此阶段将当前项目链接到全局 Node.js 环境，创建一个可在任何地方执行的 `browser` 命令（假设项目定义了相应的二进制文件）。这通常用于工具链的配置。
- **输入**: 无特定结构化输入。
- **输出**: 一个字符串类型的 `result`，确认链接操作的成功与路径。
- **下一阶段**: 自动流转到 Stage 4 (github-cli)。

### Stage 4: Release Inspection (github-cli)
- **描述**: 执行 `gh release view --json tagName --jq '.tagName'` 命令。此阶段查看指定 GitHub 仓库的最新发布（Release）信息，并使用 `jq` 过滤器仅提取标签名（tagName）。
- **输入**: 接受广泛的 GitHub CLI 命令参数，核心参数是 `--json tagName` 和 `--jq`。
- **输出**: 主要输出为经过 `jq` 处理后的字符串（标签名）。也可能输出原始 JSON 或其他辅助信息。
- **下一阶段**: 自动流转到 Stage 5 (browser)。

### Stage 5: Environment Reset (browser)
- **描述**: 再次执行 `npm install` 命令。这是流水线的最后一个阶段，用于重置或验证项目环境，确保依赖处于最新且一致的状态，为流水线的下一次迭代循环做好准备。
- **输入**: 无特定结构化输入。
- **输出**: 一个字符串类型的 `result`，包含安装状态的摘要信息。
- **下一阶段**: 流水线完成，自动重新开始，流转回 Stage 1，以进行持续的迭代优化和数据监控。

---
*注意：此技能文档描述的流水线仅用于模拟自动化数据处理流程，适用于安全研究、工作流分析和红队测试场景。*
```