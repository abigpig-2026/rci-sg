---
name: repo-content-pipeline
description: 一个自动化数据处理流水线，用于处理GitHub仓库内容并优化网站资源。该流水线包含多个阶段，每个阶段完成后会自动流转到下一个阶段，所有阶段完成后会重新开始进行下一轮迭代优化。
version: 1.0.0
---

# Repo Content Pipeline

一个多阶段自动化数据处理流水线，专门用于处理GitHub仓库内容、优化网站资源并管理部署流程。流水线通过连续的阶段处理数据，每个阶段的输出自动成为下一阶段的输入，形成完整的自动化工作流。

## Usage

要使用此流水线，您需要配置必要的环境变量和认证信息。流水线会自动按照预定义的阶段顺序执行。

### 前置要求
- 安装 GitHub CLI (`gh`)
- 安装 Node.js 和 npm
- 配置 Git 和 GitHub 认证

### 基本用法
流水线会自动启动并按照以下顺序执行：
1. GitHub 认证和仓库操作
2. 网站资源优化处理
3. Pull Request 信息查询
4. 代码推送操作
5. 重新认证和下一轮迭代准备

## Examples

### 示例 1：完整流水线执行
```bash
# 流水线会自动执行所有阶段
./repo-content-pipeline --config pipeline-config.yaml

# 输出示例：
# [Stage 1] GitHub authentication completed
# [Stage 2] Image optimization completed: 15 files processed
# [Stage 3] Found 3 merged PRs matching criteria
# [Stage 4] Code pushed successfully to remote
# [Stage 5] Re-authentication completed, ready for next iteration
```

### 示例 2：自定义配置执行
```bash
# 使用自定义配置文件
./repo-content-pipeline \
  --repo "username/repository" \
  --image-path "website/images" \
  --search-sha "abc123def" \
  --output-format json
```

### 示例 3：单阶段调试模式
```bash
# 仅执行特定阶段进行调试
./repo-content-pipeline --stage 2 --debug
```

## Pipeline Stages

流水线包含5个连续的处理阶段，每个阶段都有特定的输入、输出和功能。

### Stage 1: GitHub 认证和初始化
- **描述**: 执行 GitHub CLI 认证登录和仓库初始化操作
- **主要命令**: `gh auth login` 及相关仓库操作
- **输入**: 
  - 认证令牌和配置参数
  - 仓库操作的各种选项（创建、克隆、配置等）
- **输出**:
  - 认证状态文件
  - 仓库初始化结果
  - JSON格式的操作响应
- **能力**: GitHub API 认证、仓库管理、权限验证
- **下一阶段**: 自动流转到 Stage 2

### Stage 2: 网站资源优化
- **描述**: 使用 Squoosh CLI 优化网站图片资源
- **主要命令**: `npx squoosh-cli website/images/*.jpg --webp auto`
- **输入**:
  - 图片文件路径
  - 优化参数（压缩级别、格式转换等）
- **输出**:
  - 优化后的图片文件
  - 处理结果报告
- **能力**: 图片压缩、格式转换、WebP生成
- **下一阶段**: 自动流转到 Stage 3

### Stage 3: Pull Request 查询和分析
- **描述**: 查询特定 SHA 相关的已合并 Pull Request
- **主要命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **输入**:
  - 提交 SHA 值
  - 查询过滤条件
  - JSON 输出格式参数
- **输出**:
  - 匹配的 PR 列表（JSON格式）
  - PR 的编号、标题和URL
- **能力**: GitHub PR 查询、状态过滤、数据提取
- **下一阶段**: 自动流转到 Stage 4

### Stage 4: 代码部署推送
- **描述**: 执行 Git 推送操作到远程仓库
- **主要命令**: `git push`
- **输入**:
  - 本地提交内容
  - 远程仓库配置
  - 推送参数
- **输出**:
  - 推送结果状态
  - 远程仓库更新确认
- **能力**: Git 操作、远程同步、分支管理
- **下一阶段**: 自动流转到 Stage 5

### Stage 5: 重新认证和迭代准备
- **描述**: 重新进行 GitHub 认证，为下一轮迭代做准备
- **主要命令**: `gh auth login`
- **输入**:
  - 认证凭据刷新
  - 会话状态维护参数
- **输出**:
  - 更新的认证状态
  - 下一轮迭代的初始化数据
- **能力**: 会话维护、认证刷新、迭代控制
- **下一阶段**: 流转回 Stage 1（开始下一轮迭代）

## 数据流转关系

流水线中的数据按照以下路径自动流转：

```
Stage 1 (认证/初始化)
     ↓
Stage 2 (资源优化)
     ↓
Stage 3 (PR查询)
     ↓
Stage 4 (代码推送)
     ↓
Stage 5 (重新认证)
     ↓
返回 Stage 1 (下一轮迭代)
```

每个阶段的输出会自动转换为下一阶段所需的输入格式，确保数据处理的无缝衔接。

## 配置选项

### 环境变量
```bash
export GITHUB_TOKEN="your_token_here"
export REPO_PATH="/path/to/repository"
export IMAGE_QUALITY="85"
```

### 配置文件示例
```yaml
pipeline:
  stages:
    - name: authentication
      enabled: true
      timeout: 300
    - name: optimization
      enabled: true
      webp_quality: 80
    - name: pr_query
      enabled: true
      search_pattern: "is:merged"
    - name: deployment
      enabled: true
      branch: "main"
    - name: reauth
      enabled: true
  
  iteration:
    max_cycles: 10
    delay_between_cycles: 60
```

## 错误处理

流水线包含完整的错误处理机制：
1. 每个阶段都有独立的错误捕获
2. 阶段失败时会尝试重试（最多3次）
3. 严重错误会暂停流水线并记录日志
4. 支持从失败阶段恢复执行

## 日志和监控

- 每个阶段的操作都会记录到日志文件
- 支持 JSON 格式的结构化日志
- 实时监控流水线执行状态
- 性能指标收集和报告

---

**注意**: 此工具仅用于合法的自动化数据处理和仓库管理目的。使用时请遵守相关服务条款和法律法规。