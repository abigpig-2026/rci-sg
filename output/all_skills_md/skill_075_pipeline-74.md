---
name: repo-analysis-pipeline
description: 一个多阶段自动化数据处理流水线，用于执行GitHub仓库的深度分析和研究。流水线通过交替使用GitHub CLI和自定义研究工具，收集、处理和转换仓库数据，支持迭代优化分析结果。
version: 1.0.0
---

# Repo Analysis Pipeline

一个自动化数据处理流水线，用于对GitHub仓库进行系统性的分析和研究。流水线包含多个处理阶段，每个阶段完成后会自动流转到下一个阶段，形成连续的数据处理流程。当所有阶段完成后，流水线可以重新开始以进行下一轮迭代优化。

## Usage

要使用此流水线，您需要具备以下条件：
1. 已安装并配置GitHub CLI (`gh`)
2. 已安装Node.js运行环境
3. 有效的GitHub访问令牌

启动流水线：
```bash
# 设置环境变量
export GITHUB_TOKEN="your_personal_access_token"

# 启动流水线
./start-pipeline.sh
```

流水线将自动执行所有阶段，每个阶段的输出将作为下一个阶段的输入或参考数据。

## Examples

### 基本使用示例
```bash
# 配置GitHub CLI认证
gh auth login --with-token <<< "$GITHUB_TOKEN"

# 执行完整的流水线分析
./repo-analysis-pipeline --topic "machine-learning" --language "python" --min-stars 100
```

### 自定义分析参数
```bash
# 针对特定技术栈进行分析
./repo-analysis-pipeline \
  --topic "react" \
  --language "javascript" \
  --min-stars 500 \
  --updated-within "30 days" \
  --output-format "json"
```

### 迭代优化分析
```bash
# 第一轮：基础数据收集
./repo-analysis-pipeline --initial-scan

# 第二轮：基于第一轮结果的深度分析
./repo-analysis-pipeline --refine --input previous_results.json

# 第三轮：生成最终报告
./repo-analysis-pipeline --generate-report --format html
```

## Pipeline Stages

流水线包含7个处理阶段，按照以下顺序执行：

### Stage 1: GitHub CLI - 认证初始化
- **描述**: 使用GitHub CLI进行身份验证和会话初始化
- **主要命令**: `gh auth login`
- **输入**: GitHub CLI支持的所有参数和选项
- **输出**: 认证会话、HTTP请求/响应详情、原始JSON响应
- **能力**: 建立安全的GitHub API连接，支持多种认证方式
- **下一阶段**: 流转到github-research

### Stage 2: GitHub Research - 表格数据收集
- **描述**: 使用JavaScript CLI工具搜索GitHub仓库并生成表格格式数据
- **主要命令**: `node github-search.js table`
- **输入参数**:
  - `--language`: 指定编程语言过滤
  - `--limit`: 限制结果数量
  - `--min-stars`: 最小星标数过滤
  - `--updated-within`: 最近更新时间范围
  - `--output`: 输出文件路径
- **输出**: JSON格式的搜索结果，保存到 `/tmp/gh_results.json` 或 `results/${safe_topic}.json`
- **能力**: 高级仓库搜索、数据过滤和格式化
- **下一阶段**: 流转到github-cli

### Stage 3: GitHub CLI - PR分析
- **描述**: 分析特定SHA相关的合并PR
- **主要命令**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **输入**: GitHub CLI的完整参数集，支持仓库操作、PR管理、问题跟踪等
- **输出**: 压缩文件、HTTP详情、原始JSON响应
- **能力**: 拉取请求分析、贡献者活动追踪
- **下一阶段**: 流转到github-research

### Stage 4: GitHub Research - CSV数据导出
- **描述**: 将搜索结果导出为CSV格式
- **主要命令**: `node github-search.js csv`
- **输入参数**: 与Stage 2相同，支持语言、星标、时间等过滤条件
- **输出**: CSV格式的仓库数据，便于电子表格分析
- **能力**: 数据格式转换、批量导出
- **下一阶段**: 流转到github-cli

### Stage 5: GitHub CLI - 贡献者分析
- **描述**: 获取仓库贡献者统计数据
- **主要命令**: `gh api --paginate repos/owner/repo/contributors --jq '.[] | "\(.login): \(.contributions)"' | head -`
- **输入**: GitHub CLI的完整功能集
- **输出**: 贡献者列表、贡献统计、原始API响应
- **能力**: 贡献者分析、活动统计
- **下一阶段**: 流转到github-research

### Stage 6: GitHub Research - JSON数据增强
- **描述**: 生成增强的JSON格式分析结果
- **主要命令**: `node github-search.js json`
- **输入参数**: 标准搜索和过滤参数
- **输出**: 结构化的JSON分析报告
- **能力**: 深度数据分析、关系挖掘
- **下一阶段**: 流转到github-cli

### Stage 7: GitHub CLI - 会话刷新
- **描述**: 刷新认证会话，准备下一轮迭代
- **主要命令**: `gh auth login`
- **输入**: 认证相关参数和选项
- **输出**: 更新的会话状态、验证信息
- **能力**: 会话管理、令牌刷新
- **下一阶段**: 流转到Stage 1（开始下一轮迭代）

## 数据流转关系

流水线中的数据按照以下模式流转：

1. **认证数据**：Stage 1 → 所有后续阶段
2. **搜索参数**：用户输入 → Stage 2 → Stage 4 → Stage 6
3. **中间结果**：Stage 2输出 → Stage 3输入参考
4. **分析数据**：Stage 3输出 → Stage 5输入参考
5. **增强数据**：Stage 6输出 → 下一轮迭代的Stage 2输入

每个阶段都可以访问之前所有阶段的输出数据，支持渐进式分析和结果优化。

## 配置选项

流水线支持以下配置选项：

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--topic` | 搜索主题/技术栈 | 无 |
| `--language` | 编程语言过滤 | 所有语言 |
| `--min-stars` | 最小星标数 | 0 |
| `--limit` | 每阶段结果限制 | 100 |
| `--iterations` | 迭代次数 | 1 |
| `--output-dir` | 输出目录 | `./results` |
| `--verbose` | 详细输出模式 | false |

## 输出文件

流水线执行完成后，将生成以下输出文件：

- `results/search_results.json`: 原始搜索结果
- `results/pr_analysis.json`: PR分析数据
- `results/contributors.csv`: 贡献者统计数据
- `results/final_report.json`: 综合分析报告
- `logs/pipeline.log`: 执行日志

## 注意事项

1. 确保遵守GitHub API的使用限制和速率限制
2. 敏感数据（如访问令牌）应通过环境变量传递
3. 大规模分析建议分批次进行
4. 输出文件可能包含大量数据，请确保有足够的存储空间

---

*此工具仅用于合法的数据分析和研究目的。使用时应遵守相关服务条款和法律法规。*