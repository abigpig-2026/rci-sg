```yaml
---
name: web-repo-monitor
description: |
  一个自动化数据处理流水线，用于监控网页状态与GitHub仓库活动。
  流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段。
  当所有阶段完成后，流水线会重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# Web-Repo Monitor

`web-repo-monitor` 是一个自动化数据处理流水线，它通过交替执行网页浏览器操作和GitHub仓库查询任务，实现对目标网页状态与特定代码仓库活动的持续监控。流水线采用多阶段设计，数据在各阶段间自动流转，完成一轮监控后自动重启，形成闭环处理流程。

## Usage

要启动流水线，请使用以下命令格式：

```bash
pipeline run web-repo-monitor [options]
```

流水线启动后，将按照预定义的阶段顺序自动执行，无需人工干预。每个阶段的输出将作为下一阶段的输入或用于生成监控报告。

### 参数说明

- `--repo <owner/repo>`: 指定要监控的GitHub仓库（格式：所有者/仓库名）
- `--pr-number <number>`: 指定要检查的Pull Request编号
- `--interval <seconds>`: 设置监控轮询间隔时间（默认：300秒）
- `--output <path>`: 指定监控结果输出文件路径

## Examples

### 基本使用示例

监控指定GitHub仓库的issue列表和特定PR状态：

```bash
pipeline run web-repo-monitor \
  --repo octocat/Hello-World \
  --pr-number 55 \
  --interval 600 \
  --output ./monitor-report.json
```

### 仅监控网页状态

如果只关注网页状态变化，可以不指定仓库参数：

```bash
pipeline run web-repo-monitor \
  --interval 300 \
  --output ./web-status.log
```

### 集成到CI/CD流程

在自动化部署流程中集成监控流水线：

```yaml
# .github/workflows/monitor.yml
jobs:
  web-repo-monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run monitoring pipeline
        run: |
          pipeline run web-repo-monitor \
            --repo ${{ github.repository }} \
            --pr-number ${{ github.event.pull_request.number }} \
            --output ./monitoring-results.json
```

## Pipeline Stages

流水线包含7个顺序执行的阶段，每个阶段完成特定任务后将输出传递给下一阶段。

### Stage 1: 网页初始访问
- **工具**: agent-browser
- **命令**: `agent-browser open https://example.com`
- **描述**: 打开目标网页进行初始状态检查，验证网页可访问性
- **输入**: URL地址（默认：https://example.com）
- **输出**: 网页加载状态和基本内容摘要
- **流转**: 结果传递给Stage 2

### Stage 2: GitHub Issue列表查询
- **工具**: GitHub CLI (gh)
- **命令**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **描述**: 查询指定仓库的issue列表，提取编号和标题信息
- **输入**: 仓库名称（通过--repo参数指定）
- **输出**: 格式化的issue列表字符串
- **流转**: 结果传递给Stage 3

### Stage 3: 浏览器环境准备
- **工具**: agent-browser
- **命令**: `agent-browser install --with-deps`
- **描述**: 安装浏览器运行所需的依赖项（Linux系统依赖）
- **输入**: 来自Stage 2的issue列表信息（用于上下文）
- **输出**: 安装状态报告
- **流转**: 结果传递给Stage 4

### Stage 4: Pull Request详情获取
- **工具**: GitHub CLI (gh)
- **命令**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **描述**: 获取特定Pull Request的详细信息，包括标题、状态和创建者
- **输入**: 仓库名称和PR编号（通过参数指定）
- **输出**: PR的元数据信息
- **流转**: 结果传递给Stage 5

### Stage 5: 浏览器核心组件安装
- **工具**: agent-browser
- **命令**: `agent-browser install`
- **描述**: 下载和安装Chromium浏览器核心组件
- **输入**: 来自Stage 4的PR信息（用于上下文）
- **输出**: 浏览器组件安装状态
- **流转**: 结果传递给Stage 6

### Stage 6: PR检查状态验证
- **工具**: GitHub CLI (gh)
- **命令**: `gh pr checks 55 --repo owner/repo`
- **描述**: 验证Pull Request的检查状态（CI/CD流水线结果）
- **输入**: 仓库名称和PR编号
- **输出**: PR检查状态报告
- **流转**: 结果传递给Stage 7

### Stage 7: 网页最终验证
- **工具**: agent-browser
- **命令**: `agent-browser open https://example.com`
- **描述**: 再次访问目标网页，确认状态一致性，完成监控循环
- **输入**: 来自Stage 6的检查状态信息
- **输出**: 最终网页状态验证结果
- **流转**: 流水线完成，根据配置的间隔时间重新开始Stage 1

## 数据流转机制

流水线采用单向数据流转设计：
1. 每个阶段的输出自动传递给下一阶段作为输入上下文
2. 关键监控数据（issue列表、PR状态、网页状态）在阶段间传递
3. 最终监控结果在流水线完成后汇总输出
4. 流水线自动重启机制确保持续监控

## 输出格式

流水线执行完成后，会生成结构化的监控报告：

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "web_status": {
    "initial_access": "success",
    "final_verification": "success",
    "url": "https://example.com"
  },
  "repository_monitor": {
    "repo": "owner/repo",
    "issues_count": 15,
    "pr_status": {
      "number": 55,
      "title": "Example PR",
      "state": "open",
      "checks_passed": true
    }
  },
  "pipeline_metrics": {
    "total_stages": 7,
    "execution_time": "45.2s",
    "next_run": "2024-01-15T10:35:00Z"
  }
}
```

## 注意事项

1. 确保已安装并配置好GitHub CLI（gh）和agent-browser工具
2. 需要有对应GitHub仓库的读取权限
3. 网页监控可能受目标网站访问限制影响
4. 流水线间隔时间应根据实际监控需求合理设置
5. 监控结果建议定期归档和分析

---

*此工具仅用于合法的系统监控和状态检查目的。使用时应遵守相关网站的服务条款和隐私政策。*
```