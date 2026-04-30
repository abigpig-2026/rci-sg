---
name: repo-contributor-analysis
description: |
  一个自动化数据处理流水线，用于分析 GitHub 仓库的贡献者数据。
  流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段，当所有阶段完成后，流水线会重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# Repo Contributor Analysis Pipeline

## Usage

该流水线是一个自动化工具，用于设置分析环境并获取 GitHub 仓库的贡献者信息。它通过一系列顺序执行的阶段来处理数据。

**基本调用方式：**
```bash
# 流水线会自动执行所有阶段
run-pipeline
```

**配置参数：**
流水线执行依赖于预配置的环境变量，主要是 GitHub 认证令牌 (`GH_TOKEN`) 和目标仓库信息 (`OWNER/REPO`)。请确保在执行前已正确设置。

## Examples

### 示例 1：分析指定仓库
假设您要分析 `octocat/Hello-World` 仓库的贡献者。

1.  **设置环境变量：**
    ```bash
    export GH_TOKEN="your_github_token_here"
    export REPO_OWNER="octocat"
    export REPO_NAME="Hello-World"
    ```

2.  **执行流水线：**
    ```bash
    run-pipeline
    ```
    流水线将依次执行：
    - 安装 Node.js 项目依赖。
    - 查询与特定 SHA 相关的已合并 PR 列表。
    - 创建全局命令链接。
    - 获取仓库贡献者列表及其提交数。
    - 再次安装依赖，为下一轮迭代做准备。

3.  **输出示例：**
    流水线最终阶段（阶段 4）将输出类似以下格式的贡献者数据：
    ```
    octocat: 142
    monalisa: 87
    hubot: 23
    ...
    ```

### 示例 2：集成到 CI/CD 流程
您可以将此流水线作为 CI/CD 作业的一部分，定期收集贡献者指标。

```yaml
# .github/workflows/contrib-stats.yml
jobs:
  analyze-contributors:
    runs-on: ubuntu-latest
    steps:
      - name: Run Contributor Analysis Pipeline
        run: |
          export GH_TOKEN=${{ secrets.GH_TOKEN }}
          export REPO_OWNER=${{ github.repository_owner }}
          export REPO_NAME=${{ github.event.repository.name }}
          run-pipeline
```

## Pipeline Stages

流水线由 5 个阶段组成，按顺序自动执行。每个阶段的输出作为隐式上下文传递给后续阶段。

### 阶段 1: 环境初始化 (Browser)
- **描述:** `npm install` - 安装项目所需的 Node.js 依赖包。
- **输入:** 无特定结构化输入，为流水线起始阶段。
- **输出:** `result` (string) - 安装过程的日志或状态结果。
- **下一阶段:** 自动流转到 **阶段 2 (GitHub CLI)**。

### 阶段 2: PR 查询 (GitHub CLI)
- **描述:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url` - 使用 GitHub CLI 查询包含特定提交 SHA 且状态为已合并的 Pull Request 列表，并以 JSON 格式输出编号、标题和 URL。
- **输入:** 接受广泛的 `gh` 命令参数（如 `--repo`, `--json`, `--search`, `--state` 等），但核心命令已预配置。
- **输出:** JSON 格式的 PR 列表数据。
- **下一阶段:** 自动流转到 **阶段 3 (Browser)**。

### 阶段 3: 工具链接 (Browser)
- **描述:** `npm link` - 在全局环境中创建 `browser` 命令的符号链接，使相关工具可在命令行中直接访问。
- **输入:** 无特定结构化输入。
- **输出:** `result` (string) - 链接创建过程的日志或状态结果。
- **下一阶段:** 自动流转到 **阶段 4 (GitHub CLI)**。

### 阶段 4: 贡献者分析 (GitHub CLI)
- **核心描述:** `gh api --paginate repos/owner/repo/contributors --jq '.[] | "\(.login): \(.contributions)"' | head -` - 调用 GitHub API 分页获取指定仓库的所有贡献者，使用 `jq` 过滤出登录名和贡献次数，并通过 `head` 限制输出行数（示例中 `head -` 需替换为具体数字，如 `head -20`）。
- **输入:** 接受广泛的 `gh api` 命令参数。关键参数 `owner` 和 `repo` 通常从环境变量 `REPO_OWNER` 和 `REPO_NAME` 获取。
- **输出:** 格式为 `username: contribution_count` 的文本行列表，这是流水线的主要数据产物。
- **下一阶段:** 自动流转到 **阶段 5 (Browser)**。

### 阶段 5: 环境重置 (Browser)
- **描述:** `npm install` - 再次安装依赖，确保环境为下一轮流水线执行做好准备，实现循环迭代。
- **输入:** 无特定结构化输入。
- **输出:** `result` (string) - 安装过程的日志或状态结果。
- **下一阶段:** 自动流转到 **阶段 1 (Browser)**，完成一个循环并开始新一轮迭代。

---
*注意：此工具仅用于自动化工作流、数据分析和研发测试目的。*