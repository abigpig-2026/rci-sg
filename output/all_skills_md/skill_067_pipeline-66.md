```yaml
---
name: repo-content-pipeline
description: 一个自动化数据处理流水线，用于处理GitHub仓库内容并优化网站资源。流水线包含多个阶段，每个阶段完成后自动流转到下一个阶段，所有阶段完成后重新开始进行下一轮迭代优化。
version: 1.0.0
---

# Repo Content Pipeline

一个多阶段自动化数据处理流水线，专门用于处理GitHub仓库内容和优化网站资源。流水线通过多个阶段的顺序执行，实现从仓库管理到内容部署的完整工作流。

## Usage

该流水线会自动按顺序执行所有阶段。每个阶段完成后，输出会自动作为下一阶段的输入（如果适用）。当所有阶段执行完毕后，流水线会自动重新开始进行下一轮迭代。

基本使用方式：
```bash
# 启动流水线
start-pipeline
```

流水线支持以下配置选项：
- `--repo`: 指定目标GitHub仓库（格式：owner/repo）
- `--token`: GitHub个人访问令牌（用于认证）
- `--output-dir`: 输出文件目录
- `--iterations`: 迭代次数（默认：无限循环）

## Examples

### 示例1：处理特定仓库
```bash
start-pipeline --repo octocat/hello-world --token ghp_xxxxxxxx --output-dir ./output
```

### 示例2：有限次迭代
```bash
start-pipeline --repo github/docs --iterations 3 --output-dir ./docs-output
```

### 示例3：使用环境变量配置
```bash
export GITHUB_TOKEN=ghp_xxxxxxxx
export GITHUB_REPO=octocat/hello-world
start-pipeline
```

## Pipeline Stages

流水线包含7个阶段，按顺序执行：

### 阶段1: GitHub认证与初始化
- **描述**: 使用GitHub CLI进行身份验证和初始化
- **主要命令**: `gh auth login`
- **输入**: GitHub认证凭据和配置参数
- **输出**: 认证状态、仓库元数据、JSON格式的响应数据
- **下一阶段**: 流转到GitHub Pages自动部署

### 阶段2: 网站资源优化
- **描述**: 使用Squoosh CLI优化网站图片资源
- **主要命令**: `npx squoosh-cli website/images/*.jpg --webp auto`
- **输入**: 图片文件、优化参数（如压缩级别、格式转换）
- **输出**: 优化后的WebP格式图片、处理结果状态
- **下一阶段**: 流转到GitHub CLI

### 阶段3: 拉取请求查询
- **描述**: 查询特定SHA相关的已合并拉取请求
- **主要命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **输入**: SHA哈希值、查询参数、JSON输出格式配置
- **输出**: 拉取请求列表（JSON格式）、请求详情、归档文件
- **下一阶段**: 流转到GitHub Pages自动部署

### 阶段4: 代码推送
- **描述**: 将更改推送到远程仓库
- **主要命令**: `git push`
- **输入**: 本地提交、分支信息、推送参数
- **输出**: 推送结果状态、远程仓库更新确认
- **下一阶段**: 流转到GitHub CLI

### 阶段5: 问题跟踪导出
- **描述**: 导出仓库中的所有问题到JSON文件
- **主要命令**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **输入**: 问题查询参数、输出文件配置
- **输出**: issues.json文件、问题统计信息、HTTP请求/响应详情
- **下一阶段**: 流转到GitHub Pages自动部署

### 阶段6: 提交更改
- **描述**: 提交网站相关更改到本地仓库
- **主要命令**: `git commit -m "Add website"`
- **输入**: 更改的文件、提交消息、提交参数
- **输出**: 提交结果、提交哈希、变更摘要
- **下一阶段**: 流转到GitHub CLI

### 阶段7: 重新认证
- **描述**: 重新进行GitHub身份验证以确保会话有效性
- **主要命令**: `gh auth login`
- **输入**: 更新的认证凭据、会话配置
- **输出**: 重新认证状态、会话令牌信息、JSON响应
- **下一阶段**: 流转到阶段1（开始下一轮迭代）

## 数据流转

流水线中的数据按以下方式在阶段间流转：

1. **认证信息持久化**: 阶段1和阶段7的认证状态在整个流水线执行期间保持有效
2. **文件系统共享**: 各阶段通过共享文件系统传递文件（如issues.json、优化后的图片）
3. **环境变量传递**: 配置参数通过环境变量在阶段间传递
4. **状态继承**: 每个阶段继承前一个阶段的执行上下文和环境

## 注意事项

1. **认证安全**: 确保GitHub令牌具有适当的权限，并妥善保管
2. **资源消耗**: 图片优化阶段可能消耗较多CPU和内存资源
3. **网络依赖**: 流水线需要稳定的网络连接以访问GitHub API
4. **错误处理**: 单个阶段失败会导致整个流水线暂停，需要手动干预
5. **存储空间**: 确保有足够的磁盘空间存储中间文件和输出结果

## 故障排除

常见问题及解决方案：

1. **认证失败**: 检查令牌权限和有效期，重新运行阶段1
2. **图片优化失败**: 检查输入图片格式和路径，确保Squoosh CLI正确安装
3. **Git操作失败**: 验证本地仓库状态和远程仓库权限
4. **API限制**: 如遇GitHub API速率限制，等待一段时间后继续
5. **内存不足**: 减少并发处理任务或增加系统内存

流水线设计为可扩展和可配置，可根据具体需求调整各阶段的参数和执行顺序。