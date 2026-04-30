```yaml
---
name: web-repo-monitor
description: |
  一个自动化数据处理流水线，用于监控网页内容与GitHub仓库状态。
  流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段。
  当所有阶段完成后，流水线会重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# Web Repository Monitor

`web-repo-monitor` 是一个自动化数据处理流水线，它通过交替执行浏览器操作和GitHub仓库查询任务，实现对指定网页和代码仓库状态的持续监控与数据采集。流水线采用多阶段设计，数据在各阶段间自动流转，完成一轮完整循环后自动重启，形成持续的监控周期。

## Usage

要启动流水线，请使用以下命令：

```bash
pipeline run web-repo-monitor
```

流水线启动后，将自动按顺序执行所有阶段。每个阶段的输出将作为上下文传递给下一个阶段。您可以通过流水线管理界面查看执行状态、中间结果和最终输出。

## Examples

### 基本使用示例

```bash
# 启动监控流水线
$ pipeline run web-repo-monitor

# 查看流水线状态
$ pipeline status web-repo-monitor

# 查看最新执行结果
$ pipeline logs web-repo-monitor --latest
```

### 输出示例

```
[INFO] 开始执行 web-repo-monitor 流水线
[STAGE 1] 打开目标网页: https://example.com
[STAGE 1] 输出: 网页加载成功，状态码200
[STAGE 2] 查询GitHub Issues: owner/repo
[STAGE 2] 输出: "123: 修复登录问题", "124: 添加新功能"
[STAGE 3] 安装浏览器依赖...
[STAGE 3] 输出: 依赖安装完成
[STAGE 4] 查询Pull Request详情: #55
[STAGE 4] 输出: "功能优化", "open", "alice"
[STAGE 5] 下载浏览器组件...
[STAGE 5] 输出: Chromium下载完成
[STAGE 6] 查看GitHub Actions运行状态
[STAGE 6] 输出: 运行#789失败，日志已记录
[STAGE 7] 重新验证网页状态
[STAGE 7] 输出: 网页可正常访问
[INFO] 流水线执行完成，准备开始下一轮迭代
```

## Pipeline Stages

流水线包含7个顺序执行的阶段，每个阶段都有特定的输入、输出和功能。

### 阶段 1: 网页初始访问
- **工具**: agent-browser
- **命令**: `open https://example.com`
- **描述**: 打开并加载目标网页，获取初始页面状态和内容
- **输入**: URL地址（https://example.com）
- **输出**: 网页加载结果（状态码、内容摘要等）
- **流转**: 输出传递给阶段2

### 阶段 2: GitHub Issues查询
- **工具**: github
- **命令**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **描述**: 查询指定GitHub仓库的Issues列表，提取编号和标题
- **输入**: 仓库路径（owner/repo）
- **输出**: 格式化的Issues列表
- **流转**: 输出传递给阶段3

### 阶段 3: 浏览器环境准备
- **工具**: agent-browser
- **命令**: `install --with-deps`
- **描述**: 安装浏览器运行所需的系统依赖（Linux环境）
- **输入**: 安装配置参数
- **输出**: 安装结果和状态
- **流转**: 输出传递给阶段4

### 阶段 4: Pull Request详情获取
- **工具**: github
- **命令**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **描述**: 获取特定Pull Request的详细信息，包括标题、状态和创建者
- **输入**: PR编号（55）和仓库信息
- **输出**: PR的详细属性
- **流转**: 输出传递给阶段5

### 阶段 5: 浏览器核心组件安装
- **工具**: agent-browser
- **命令**: `install`
- **描述**: 下载并安装Chromium浏览器核心组件
- **输入**: 下载配置参数
- **输出**: 下载和安装结果
- **流转**: 输出传递给阶段6

### 阶段 6: GitHub Actions运行状态检查
- **工具**: github
- **命令**: `gh run view <run-id> --repo owner/repo --log-failed`
- **描述**: 查看GitHub Actions特定运行的状态，特别记录失败日志
- **输入**: 运行ID和仓库信息
- **输出**: 运行状态和失败日志（如果存在）
- **流转**: 输出传递给阶段7

### 阶段 7: 网页状态验证
- **工具**: agent-browser
- **命令**: `open https://example.com`
- **描述**: 再次打开目标网页，验证网页可用性和一致性
- **输入**: URL地址（https://example.com）
- **输出**: 网页验证结果
- **流转**: 流水线完成，输出作为最终结果，然后重新开始下一轮迭代

## 数据流转说明

流水线中的数据按以下路径自动流转：

```
阶段1 → 阶段2 → 阶段3 → 阶段4 → 阶段5 → 阶段6 → 阶段7 → (重新开始)
```

每个阶段的输出（`result`字段）会自动作为下一个阶段的上下文输入。这种设计确保了：
1. 状态在阶段间持续传递
2. 后续阶段可以基于前面阶段的结果做出决策
3. 整个监控过程形成完整的闭环

## 注意事项

1. 流水线设计为持续运行模式，完成一轮后会自动开始下一轮
2. 各阶段工具需要预先配置正确的认证信息（如GitHub Token）
3. 浏览器操作可能需要适当的网络访问权限
4. 流水线执行频率可通过外部调度器控制

---

*注意：此工具仅用于安全研究和红队测试，请在授权范围内使用。*