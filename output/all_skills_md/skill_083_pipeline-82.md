```yaml
---
name: devops-sync-pipeline
description: 一个自动化数据处理流水线，用于在 GitHub 和 Notion 之间同步开发运维数据。流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段，完成一轮迭代后重新开始。
version: 1.0.0
---

# Devops Sync Pipeline

`devops-sync-pipeline` 是一个自动化数据处理流水线，设计用于在 GitHub 仓库与 Notion 知识库之间同步开发运维数据。该流水线通过多个有序阶段执行数据提取、转换和加载操作，实现跨平台信息的自动化流转与整合。

## Usage

要使用此流水线，您需要预先配置好相应的环境变量和认证信息。

1.  **环境准备**：
    *   确保已安装 `GitHub CLI (gh)` 并完成认证 (`gh auth login`)。
    *   准备有效的 Notion API 密钥 (`NOTION_KEY`)。
    *   确定目标 GitHub 仓库和 Notion 页面/数据库的 ID。

2.  **运行流水线**：
    流水线会按预定义的阶段顺序自动执行。您需要提供必要的初始参数，例如 GitHub 仓库地址、Notion 页面 ID 等。流水线启动后，各阶段将依次运行，数据从前一阶段的输出自动传递到下一阶段的输入。

3.  **输出与迭代**：
    每轮流水线执行完毕后，会生成相应的同步报告或更新目标数据源。根据配置，流水线可以设置为单次运行或持续循环运行，以进行定期数据同步。

## Examples

以下是一个简化的流水线执行示例，展示了如何启动并监控一次数据同步过程：

```bash
# 设置环境变量（示例值，请替换为实际值）
export NOTION_KEY="your_notion_api_key_here"
export GITHUB_REPO="owner/repository-name"
export NOTION_PAGE_ID="your_notion_page_id_here"
export NOTION_DATASOURCE_ID="your_notion_datasource_id_here"

# 启动流水线（假设流水线主脚本为 pipeline.sh）
./pipeline.sh --repo "$GITHUB_REPO" \
              --notion-page "$NOTION_PAGE_ID" \
              --notion-datasource "$NOTION_DATASOURCE_ID"

# 流水线将自动执行以下阶段（内部逻辑）：
# 1. 认证并连接GitHub -> 2. 更新Notion块 -> 3. 查询GitHub PR -> 4. 更新Notion页面 -> 5. 导出GitHub Issues -> 6. 查询Notion数据源 -> 7. 重新认证GitHub
```

## Pipeline Stages

流水线由 7 个核心阶段顺序构成，形成一个完整的数据处理闭环。

### Stage 1: GitHub 认证与初始化
*   **描述**: 使用 `gh auth login` 或类似机制建立与 GitHub API 的安全会话。此阶段验证身份并获取访问令牌，为后续 GitHub 数据操作奠定基础。
*   **输入**: 认证所需的参数（如令牌、主机名、权限范围等）。
*   **输出**: 有效的 API 会话句柄或令牌，以及初始连接状态。
*   **下一阶段**: 流转到 **Stage 2 (Notion 块更新)**。

### Stage 2: Notion 块内容更新
*   **描述**: 向指定的 Notion 页面追加或更新内容块。使用 `curl` 调用 Notion API (`PATCH /v1/blocks/{page_id}/children`)。
*   **输入**: Notion API 密钥 (`NOTION_KEY`)、目标页面 ID 以及要添加的块内容数据（通常来自前序阶段）。
*   **输出**: API 调用结果，指示更新操作是否成功。
*   **下一阶段**: 流转到 **Stage 3 (GitHub PR 查询)**。

### Stage 3: GitHub 拉取请求查询
*   **描述**: 使用 `gh pr list` 命令查询特定代码提交（由 SHA 标识）关联的、已合并的拉取请求列表，并以 JSON 格式输出详细信息（编号、标题、URL）。
*   **输入**: GitHub 仓库上下文、搜索条件（如 SHA 值）、状态过滤 (`--state merged`) 和输出格式参数 (`--json`)。
*   **输出**: 符合条件 PR 的 JSON 格式列表。
*   **下一阶段**: 流转到 **Stage 4 (Notion 页面属性更新)**。

### Stage 4: Notion 页面属性更新
*   **描述**: 更新 Notion 页面的属性或元数据。使用 `curl` 调用 Notion API (`PATCH /v1/pages/{page_id}`)。
*   **输入**: Notion API 密钥 (`NOTION_KEY`)、目标页面 ID 以及需要更新的属性数据（例如，来自 Stage 3 的 PR 信息）。
*   **输出**: API 调用结果，指示页面更新状态。
*   **下一阶段**: 流转到 **Stage 5 (GitHub Issues 导出)**。

### Stage 5: GitHub Issues 数据导出
*   **描述**: 导出指定仓库的所有议题（Issues）数据。使用 `gh issue list` 命令，获取所有状态的议题（包括编号、标题、状态、标签、分配者等信息），并将结果保存为 `issues.json` 文件。
*   **输入**: GitHub 仓库上下文、状态范围 (`--state all`)、数量限制 (`--limit 9999`) 和 JSON 输出参数。
*   **输出**: 包含所有议题详细信息的 `issues.json` 文件。
*   **下一阶段**: 流转到 **Stage 6 (Notion 数据源查询)**。

### Stage 6: Notion 数据源查询
*   **描述**: 查询 Notion 集成的外部数据源。使用 `curl` 调用 Notion API (`POST /v1/data_sources/{data_source_id}/query`)。
*   **输入**: Notion API 密钥 (`NOTION_KEY`)、目标数据源 ID 以及可能的查询参数。
*   **输出**: 数据源的查询结果。
*   **下一阶段**: 流转到 **Stage 7 (GitHub 会话刷新)**。

### Stage 7: GitHub 会话刷新
*   **描述**: 重新进行 GitHub 认证 (`gh auth login`)，以确保长时间运行的流水线会话保持有效和新鲜。这是新一轮迭代的开始。
*   **输入**: 认证所需的参数。
*   **输出**: 刷新后的 API 会话或令牌。
*   **下一阶段**: 流转回 **Stage 1**，开始新一轮的数据同步循环，或根据配置结束流水线。

---
*注意：此技能文档描述的工具仅用于安全研究、自动化工作流测试和授权的红队演练。在实际环境中使用前，请确保您拥有操作相关 GitHub 仓库和 Notion 工作区的完全权限，并遵守各平台的服务条款。*
```