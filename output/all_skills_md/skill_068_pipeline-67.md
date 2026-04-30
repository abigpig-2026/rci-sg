---
name: repo-sync-deploy
description: 一个自动化数据处理流水线，用于同步GitHub仓库数据并部署到GitHub Pages。流水线包含多个阶段，每个阶段完成后自动流转到下一个阶段，所有阶段完成后重新开始迭代优化。
version: 1.0.0
---

# Repo Sync & Deploy Pipeline

`repo-sync-deploy` 是一个自动化数据处理流水线，专门用于处理GitHub仓库数据并与GitHub Pages部署流程集成。该流水线通过一系列有序的阶段，自动化执行身份验证、数据查询、图像处理和代码部署任务。每个阶段处理完成后，其输出将作为下一个阶段的输入或触发条件，实现全自动化的数据流转和处理循环。

## Usage

要使用此流水线，您需要配置必要的环境变量和凭据。流水线会自动按顺序执行所有阶段。

**基本调用：**
```bash
# 启动流水线（通常由调度器或事件触发）
run-pipeline repo-sync-deploy
```

**配置环境变量：**
```bash
export GITHUB_TOKEN="your_personal_access_token"
export REPO_OWNER="your_username"
export REPO_NAME="your_repository"
```

流水线启动后，将自动执行以下阶段序列，并在完成后重新开始新一轮迭代。

## Examples

### 示例1：完整流水线执行
此示例展示了流水线一次完整迭代的执行过程。

```bash
# 初始化环境
export GITHUB_TOKEN="ghp_abc123..."
export TARGET_SHA="a1b2c3d4e5f6"

# 执行流水线
run-pipeline repo-sync-deploy --env GITHUB_TOKEN=$GITHUB_TOKEN --param SHA=$TARGET_SHA

# 输出示例：
# [STAGE 1] Authenticating with GitHub... SUCCESS
# [STAGE 2] Processing website images... COMPLETED
# [STAGE 3] Querying merged PRs for SHA a1b2c3d4e5f6... FOUND 2 PRs
# [STAGE 4] Pushing changes to remote... PUSHED
# [STAGE 5] Exporting issue list... WRITTEN to issues.json
# [STAGE 6] Staging local changes... ADDED 5 files
# [STAGE 7] Re-authenticating... SUCCESS
# [PIPELINE] Iteration completed. Restarting...
```

### 示例2：自定义查询参数
您可以通过参数自定义流水线中特定阶段的查询条件。

```bash
# 只查询特定状态的PR和Issue
run-pipeline repo-sync-deploy \
  --param PR_STATE="merged" \
  --param ISSUE_STATE="open" \
  --param LIMIT=50
```

## Pipeline Stages

流水线包含7个顺序执行的阶段，形成一个闭环处理流程。

### Stage 1: GitHub 身份验证
- **描述**: 使用GitHub CLI进行身份验证 (`gh auth login`)
- **输入**: GitHub CLI支持的所有参数选项，包括认证令牌、主机名、权限范围等
- **输出**: 认证状态、令牌信息、HTTP请求/响应详情，以及可能的JSON格式原始响应
- **下一阶段**: 认证成功后自动流转到 **Stage 2**
- **功能**: 建立与GitHub API的安全连接，为后续操作提供身份验证凭据

### Stage 2: 图像优化处理
- **描述**: 使用Squoosh CLI优化网站图像 (`npx squoosh-cli website/images/*.jpg --webp auto`)
- **输入**: 图像处理参数，包括WebP转换选项、空白压缩等
- **输出**: 处理结果状态字符串
- **下一阶段**: 处理完成后自动流转到 **Stage 3**
- **功能**: 自动优化网站目录中的JPEG图像，转换为WebP格式以提升页面加载性能

### Stage 3: PR数据查询
- **描述**: 查询特定SHA关联的已合并PR (`gh pr list --search "SHA_HERE" --state merged --json number,title,url`)
- **输入**: GitHub PR查询的所有参数选项，包括搜索条件、状态过滤、JSON输出格式等
- **输出**: PR列表数据，可输出为JSON格式、归档文件或原始HTTP响应
- **下一阶段**: 查询完成后自动流转到 **Stage 4**
- **功能**: 根据提供的提交SHA值，检索所有相关的已合并拉取请求，用于变更追踪和审计

### Stage 4: 代码推送部署
- **描述**: 将本地更改推送到远程仓库 (`git push`)
- **输入**: Git推送命令的相关参数
- **输出**: 推送操作结果状态字符串
- **下一阶段**: 推送成功后自动流转到 **Stage 5**
- **功能**: 将Stage 2优化的图像和Stage 6暂存的更改推送到远程仓库，触发可能的GitHub Pages构建

### Stage 5: Issue数据导出
- **描述**: 导出仓库Issue列表到JSON文件 (`gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`)
- **输入**: GitHub Issue查询的所有参数选项，包括状态过滤、数量限制、字段选择等
- **输出**: Issue数据JSON文件，包含编号、标题、状态、标签和分配者等信息
- **下一阶段**: 导出完成后自动流转到 **Stage 6**
- **功能**: 全面导出仓库的所有Issue，用于数据分析、报告生成或备份目的

### Stage 6: 更改暂存
- **描述**: 暂存所有本地更改 (`git add .`)
- **输入**: Git添加命令的相关参数
- **输出**: 暂存操作结果状态字符串
- **下一阶段**: 暂存完成后自动流转到 **Stage 7**
- **功能**: 将工作目录中的所有更改（包括优化的图像和可能的配置文件更新）添加到暂存区，准备提交

### Stage 7: 身份验证刷新
- **描述**: 刷新GitHub身份验证 (`gh auth login`)
- **输入**: 与Stage 1相同的认证参数选项
- **输出**: 与Stage 1相同的输出类型
- **下一阶段**: 认证刷新后自动流转回 **Stage 1**，开始新一轮迭代
- **功能**: 确保认证令牌的有效性，为流水线的持续运行提供持久的身份验证状态

## 数据流转关系

流水线中的数据按以下路径流转：

1. **认证凭据流转**: Stage 1和Stage 7生成的认证状态被所有需要GitHub API访问的阶段共享
2. **文件系统更改**: Stage 2生成的优化图像被Stage 6暂存，然后被Stage 4推送到远程
3. **数据文件传递**: Stage 5导出的`issues.json`文件可被外部系统或后续迭代使用
4. **查询参数传递**: Stage 3使用的SHA参数通常来自前一次迭代的提交或外部输入
5. **状态标记传递**: 每个阶段的成功/失败状态决定下一个阶段是否执行

## 迭代优化机制

流水线设计为循环执行模式：
- 当所有7个阶段完成后，流水线自动重新从Stage 1开始
- 每次迭代可以使用前一次迭代的输出作为输入（如新的提交SHA）
- 迭代间隔可通过外部调度器控制
- 失败阶段会中断当前迭代，根据配置决定是否重试或跳过

这种设计使得流水线能够持续监控仓库变化，自动处理新提交，并保持部署内容的最新状态。