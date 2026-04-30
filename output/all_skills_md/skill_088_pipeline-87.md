---
name: repo-analysis-pipeline
description: 一个自动化数据处理流水线，用于收集和分析GitHub仓库的元数据、问题和发布信息。流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段，并在所有阶段完成后重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# Repo Analysis Pipeline

一个多阶段自动化数据处理流水线，用于从GitHub仓库收集和分析数据。流水线通过浏览器代理和GitHub CLI工具的组合，依次执行数据抓取、处理和汇总任务，实现端到端的仓库分析工作流。

## Usage

要使用此流水线，需要确保环境中已安装并配置好以下工具：
- `agent-browser`：用于网页浏览和自动化操作
- `gh` (GitHub CLI)：用于与GitHub API交互

流水线会自动按照预定义的阶段顺序执行，每个阶段的输出将作为下一个阶段的输入或上下文。流水线完成后会自动重新开始，形成持续的数据处理循环。

### 基本使用

启动流水线后，它将自动执行以下流程：
1. 初始化浏览器会话并访问目标网站
2. 使用GitHub CLI查询合并的Pull Request
3. 安装必要的依赖项
4. 获取仓库的所有Issue信息
5. 下载浏览器运行时
6. 查看最新的发布标签
7. 完成数据收集并准备下一轮迭代

## Examples

### 示例1：完整运行流水线

```bash
# 启动流水线（假设流水线已配置为自动化工具）
./repo-analysis-pipeline start

# 流水线将输出类似以下信息：
# [Stage 1] Opening browser to https://example.com
# [Stage 2] Querying merged PRs with SHA: abc123...
# [Stage 3] Installing system dependencies...
# [Stage 4] Collecting issue data...
# [Stage 5] Downloading Chromium...
# [Stage 6] Checking latest release tag...
# [Stage 7] Finalizing data collection...
# [Pipeline Complete] Starting next iteration...
```

### 示例2：监控特定仓库的数据变化

```bash
# 配置目标仓库
export GITHUB_REPO="owner/repository"
export ANALYSIS_INTERVAL=3600  # 每小时的迭代间隔

# 运行流水线
./repo-analysis-pipeline --repo "$GITHUB_REPO" --interval "$ANALYSIS_INTERVAL"
```

### 示例3：导出分析结果

```bash
# 运行流水线并将结果导出到文件
./repo-analysis-pipeline --output-format json --output-file analysis_results.json
```

## Pipeline Stages

流水线包含7个连续的处理阶段，每个阶段都有特定的输入、输出和功能：

### 阶段 1: 浏览器初始化
- **工具**: agent-browser
- **命令**: `agent-browser open https://example.com`
- **功能**: 初始化浏览器会话并访问指定的URL，为后续的数据收集任务建立基础环境
- **输入**: URL、会话配置参数
- **输出**: 浏览器会话结果（字符串格式）
- **下一阶段**: 流转到github-cli

### 阶段 2: PR数据收集
- **工具**: github-cli
- **命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **功能**: 查询指定SHA相关的已合并Pull Request，收集PR编号、标题和URL信息
- **输入**: GitHub仓库上下文、搜索参数
- **输出**: JSON格式的PR数据列表，可导出为文件或直接处理
- **下一阶段**: 流转到agent-browser

### 阶段 3: 依赖安装
- **工具**: agent-browser
- **命令**: `agent-browser install --with-deps`
- **功能**: 安装必要的系统依赖项（Linux环境下），确保后续阶段的正常运行
- **输入**: 安装配置参数
- **输出**: 安装结果状态（字符串格式）
- **下一阶段**: 流转到github-cli

### 阶段 4: Issue数据收集
- **工具**: github-cli
- **命令**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **功能**: 收集仓库的所有Issue信息，包括状态、标签和分配者，并将结果保存到文件
- **输入**: 仓库上下文、查询参数
- **输出**: issues.json文件，包含完整的Issue数据集
- **下一阶段**: 流转到agent-browser

### 阶段 5: 浏览器运行时准备
- **工具**: agent-browser
- **命令**: `agent-browser install`
- **功能**: 下载和配置Chromium浏览器运行时，确保浏览器自动化功能的可用性
- **输入**: 下载配置参数
- **输出**: 下载和安装结果（字符串格式）
- **下一阶段**: 流转到github-cli

### 阶段 6: 发布信息查询
- **工具**: github-cli
- **命令**: `gh release view --json tagName --jq '.tagName'`
- **功能**: 查询仓库的最新发布标签名称，用于版本追踪和发布分析
- **输入**: 仓库发布上下文
- **输出**: 最新发布标签名称（字符串格式）
- **下一阶段**: 流转到agent-browser

### 阶段 7: 数据汇总完成
- **工具**: agent-browser
- **命令**: `agent-browser open https://example.com`
- **功能**: 完成数据收集流程，准备数据汇总和下一轮迭代的初始化
- **输入**: 汇总配置参数
- **输出**: 处理完成结果（字符串格式）
- **下一阶段**: 流转到阶段1（开始下一轮迭代）

## 数据流转

流水线中的数据按照以下路径流转：
1. 浏览器会话状态在阶段1、3、5、7之间传递
2. GitHub数据（PR、Issue、Release）在阶段2、4、6中收集并处理
3. 每个阶段的输出为下一个阶段提供必要的上下文或输入数据
4. 最终所有收集的数据在阶段7汇总，为下一轮迭代做准备

## 配置选项

流水线支持以下配置参数：
- `--target-url`: 指定初始访问的URL（默认：https://example.com）
- `--github-repo`: 指定分析的GitHub仓库
- `--output-dir`: 指定数据输出目录
- `--iteration-count`: 指定迭代次数（默认：无限循环）
- `--interval`: 指定迭代间隔时间（秒）

## 输出格式

流水线生成的数据包括：
1. PR数据：JSON格式，包含number、title、url字段
2. Issue数据：JSON格式文件，包含number、title、state、labels、assignees字段
3. Release数据：最新标签名称字符串
4. 处理日志：各阶段的执行状态和结果

---

*注意：此工具仅用于安全研究和红队测试目的。使用前请确保遵守相关服务条款和法律法规。*