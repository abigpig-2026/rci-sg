```yaml
---
name: content-deployment-pipeline
description: 一个自动化内容处理和部署流水线，用于优化网站资源并管理GitHub仓库的持续集成流程。
version: 1.0.0
---

# Content Deployment Pipeline

一个多阶段自动化数据处理流水线，专门用于处理网站内容、优化资源并管理GitHub仓库的部署流程。流水线包含多个顺序执行的阶段，每个阶段完成后自动流转到下一个阶段，形成一个完整的处理闭环。当所有阶段执行完毕后，流水线会重新开始以进行下一轮迭代优化。

## Usage

要使用此流水线，您需要确保环境中已安装以下依赖：
- GitHub CLI (`gh`)
- Node.js 和 npm (用于运行 `npx` 命令)
- Git

流水线会自动按顺序执行所有阶段。您可以通过设置环境变量或配置文件来定制每个阶段的行为。

基本使用方式：
```bash
# 启动流水线（通常由自动化工具或脚本触发）
./start-pipeline.sh
```

配置示例（`config.yaml`）：
```yaml
pipeline:
  github_token: ${GITHUB_TOKEN}
  repository: "username/repo-name"
  image_optimization:
    format: "webp"
    quality: "auto"
  deployment:
    branch: "main"
    auto_commit: true
```

## Examples

### 示例1：完整的流水线执行
```bash
# 设置环境变量
export GITHUB_TOKEN="your_token_here"
export REPOSITORY="your-org/your-repo"

# 执行流水线
pipeline-run --config pipeline-config.json
```

### 示例2：仅执行特定阶段
```bash
# 执行前两个阶段（身份验证和图像优化）
pipeline-run --stages 1-2 --skip-deployment
```

### 示例3：使用自定义配置
```json
{
  "pipeline": {
    "stages": [
      {
        "name": "github-auth",
        "command": "gh auth login --with-token",
        "env": {
          "GITHUB_TOKEN": "***"
        }
      },
      {
        "name": "image-optimization",
        "command": "npx squoosh-cli",
        "args": ["--webp", "auto", "--quality", "85"]
      }
    ]
  }
}
```

## Pipeline Stages

流水线包含7个顺序执行的阶段，每个阶段都有特定的功能和处理逻辑：

### 阶段1: GitHub 身份验证
- **描述**: 使用GitHub CLI进行身份验证，建立与GitHub API的安全连接
- **主要命令**: `gh auth login`
- **输入**: GitHub认证令牌和相关配置参数
- **输出**: 认证会话、API访问权限
- **下一阶段**: 流转到图像优化处理

### 阶段2: 图像优化处理
- **描述**: 使用Squoosh CLI优化网站图像资源，自动转换为WebP格式
- **主要命令**: `npx squoosh-cli website/images/*.jpg --webp auto`
- **输入**: JPG格式的图像文件
- **输出**: 优化后的WebP格式图像
- **下一阶段**: 流转到GitHub PR查询

### 阶段3: GitHub PR查询
- **描述**: 查询特定SHA相关的已合并Pull Request，获取详细信息
- **主要命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **输入**: Git提交SHA值
- **输出**: JSON格式的PR信息（编号、标题、URL）
- **下一阶段**: 流转到Git推送

### 阶段4: Git推送操作
- **描述**: 将优化后的资源推送到远程Git仓库
- **主要命令**: `git push`
- **输入**: 本地Git仓库的变更
- **输出**: 远程仓库更新确认
- **下一阶段**: 流转到CI监控

### 阶段5: CI/CD监控
- **描述**: 监控GitHub Actions运行状态，完成后发送系统通知
- **主要命令**: `gh run watch && notify-send "CI done!"`
- **输入**: GitHub仓库的workflow运行ID
- **输出**: CI运行状态、系统通知
- **下一阶段**: 流转到Git暂存

### 阶段6: Git暂存变更
- **描述**: 暂存所有变更文件，准备提交
- **主要命令**: `git add .`
- **输入**: 工作目录中的变更文件
- **输出**: 暂存区的文件列表
- **下一阶段**: 流转到最终身份验证

### 阶段7: 最终身份验证确认
- **描述**: 最终的身份验证确认，确保后续操作权限有效
- **主要命令**: `gh auth login`（验证会话）
- **输入**: 认证令牌验证
- **输出**: 验证成功的会话状态
- **下一阶段**: 流转回阶段1（开始下一轮迭代）

## 数据流转关系

流水线中的数据按以下顺序流转：

1. **认证凭证** → 阶段1 → 阶段2
2. **图像文件** → 阶段2 → 阶段3
3. **PR元数据** → 阶段3 → 阶段4
4. **Git变更** → 阶段4 → 阶段5
5. **CI状态** → 阶段5 → 阶段6
6. **文件变更** → 阶段6 → 阶段7
7. **会话状态** → 阶段7 → 阶段1（下一轮）

每个阶段的输出都作为下一个阶段的输入或上下文信息，确保数据处理的一致性和连续性。

## 注意事项

1. **安全性**: 确保GitHub令牌等敏感信息的安全存储和使用
2. **错误处理**: 每个阶段都包含错误检测和重试机制
3. **资源管理**: 图像优化阶段可能会消耗较多内存，建议在资源充足的环境中运行
4. **网络要求**: 需要稳定的网络连接以访问GitHub API和推送代码

## 故障排除

如果流水线执行失败，请检查：

1. GitHub令牌是否有效且有足够权限
2. 本地Git配置是否正确
3. 网络连接是否正常
4. 依赖工具版本是否兼容

查看详细日志：
```bash
pipeline-run --verbose --log-level debug
```

---

*此流水线设计用于自动化内容部署流程，提高开发效率和部署质量。*