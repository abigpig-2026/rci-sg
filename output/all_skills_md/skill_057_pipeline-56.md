```yaml
---
name: web-repo-monitor
description: |
  一个自动化数据处理流水线，用于监控网页内容与GitHub仓库状态。
  流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段。
  当所有阶段完成后，流水线会重新开始以进行下一轮迭代优化。
version: 1.0.0
---

# Web-Repo Monitor

`web-repo-monitor` 是一个自动化数据处理流水线，它通过交替执行网页浏览器操作和GitHub仓库查询任务，实现对指定网页和代码仓库状态的持续监控与数据采集。流水线各阶段自动流转，形成闭环处理流程，适用于自动化巡检、状态同步和数据聚合场景。

## Usage

要启动流水线，请使用以下命令格式：

```bash
<your-tool> run web-repo-monitor [参数]
```

流水线启动后，将按照预定义的阶段顺序自动执行，每个阶段的输出将作为下一阶段的输入或上下文。一轮执行完成后，流水线会自动重启，开始新一轮的数据处理。

## Examples

### 基本使用示例

```bash
# 启动web-repo-monitor流水线
<your-tool> run web-repo-monitor

# 带参数启动（示例）
<your-tool> run web-repo-monitor --repo "owner/repository-name" --url "https://target-site.com"
```

### 输出示例

```
[STAGE 1] 打开目标网页: https://example.com
页面加载成功，获取到页面标题: "Example Domain"

[STAGE 2] 查询GitHub Issues
123: 修复登录页面样式问题
124: 添加用户认证功能
125: API响应时间优化

[STAGE 3] 安装浏览器依赖
系统依赖安装完成，Chromium环境就绪

[STAGE 4] 查询特定PR状态
"用户认证模块重构", "open", "alice-dev"

[STAGE 5] 下载浏览器核心
Chromium v115.0.5790.170 下载完成

[STAGE 6] 查看CI运行状态
Run #456: tests - ✅ 通过
Run #457: build - ❌ 失败 (编译错误)

[STAGE 7] 重新打开网页验证
页面验证成功，状态码: 200

[PIPELINE] 一轮执行完成，开始下一轮迭代...
```

## Pipeline Stages

流水线包含7个顺序执行阶段，各阶段功能如下：

### 阶段 1: 网页初始访问
- **工具**: agent-browser
- **命令**: `open https://example.com`
- **描述**: 打开指定的目标网页，获取初始页面内容
- **输入**: URL地址
- **输出**: 网页内容或状态信息
- **流转**: 完成后自动流转到阶段2

### 阶段 2: GitHub Issues查询
- **工具**: github
- **命令**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **描述**: 查询指定仓库的Issues列表，提取编号和标题
- **输入**: 仓库名称(owner/repo格式)
- **输出**: 格式化后的Issues列表
- **流转**: 完成后自动流转到阶段3

### 阶段 3: 浏览器环境准备
- **工具**: agent-browser
- **命令**: `install --with-deps`
- **描述**: 安装浏览器运行所需的系统依赖（Linux环境）
- **输入**: 安装配置参数
- **输出**: 安装结果状态
- **流转**: 完成后自动流转到阶段4

### 阶段 4: GitHub PR详情查询
- **工具**: github
- **命令**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **描述**: 查询特定Pull Request的详细信息
- **输入**: PR编号和仓库信息
- **输出**: PR标题、状态和创建者
- **流转**: 完成后自动流转到阶段5

### 阶段 5: 浏览器核心下载
- **工具**: agent-browser
- **命令**: `install`
- **描述**: 下载Chromium浏览器核心组件
- **输入**: 下载配置参数
- **输出**: 下载完成状态
- **流转**: 完成后自动流转到阶段6

### 阶段 6: GitHub Actions运行状态
- **工具**: github
- **命令**: `gh run view <run-id> --repo owner/repo --log-failed`
- **描述**: 查看指定CI/CD运行的状态和日志（特别是失败情况）
- **输入**: 运行ID和仓库信息
- **输出**: 运行状态和错误日志
- **流转**: 完成后自动流转到阶段7

### 阶段 7: 网页二次验证
- **工具**: agent-browser
- **命令**: `open https://example.com`
- **描述**: 重新打开目标网页，验证页面可访问性和一致性
- **输入**: URL地址
- **输出**: 验证结果
- **流转**: 完成后流水线一轮结束，自动重启开始下一轮迭代

## 数据流转说明

流水线采用线性流转模式：
1. 每个阶段执行完成后，其输出结果会被记录到流水线上下文
2. 下一阶段可以访问之前所有阶段的输出作为参考
3. 阶段间没有直接的参数传递，但共享执行上下文
4. 第7阶段完成后，流水线清空上下文并重新从阶段1开始

## 注意事项

1. 确保在执行前配置好必要的认证信息（如GitHub Token）
2. 网页访问可能受到目标站点访问策略限制
3. 流水线执行频率建议根据实际需求调整
4. 监控敏感目标时请遵守相关法律法规和服务条款

---

*此技能文档描述了`web-repo-monitor`流水线的功能和使用方法。实际执行时，请确保您有权限访问相关资源。*