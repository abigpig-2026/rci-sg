```yaml
---
name: repo-analysis-pipeline
description: |
  A multi-stage automated data processing pipeline for GitHub repository analysis.
  The pipeline orchestrates browser automation and GitHub CLI operations to collect
  and process repository metadata, issues, pull requests, and contributor data.
  After completing all stages, the pipeline automatically restarts for continuous
  iterative optimization.
version: 1.0.0
---

# Repo Analysis Pipeline

## Usage

The pipeline is designed to run automatically once initiated. It requires a valid GitHub repository URL as the initial input. The pipeline will proceed through all stages sequentially, with each stage's output serving as input or context for the next.

**Prerequisites:**
- Valid GitHub personal access token (with `repo` scope) configured for `gh` CLI
- `agent-browser` installed and available in PATH
- `npm` installed (for global package management)

**Basic Execution:**
```bash
# The pipeline is triggered by providing a target repository URL
# The system will automatically sequence through all stages
echo "https://github.com/owner/repo" | start-pipeline
```

## Examples

### Example 1: Basic Repository Analysis
```bash
# Analyze a specific repository
./repo-analysis-pipeline --repo https://github.com/microsoft/vscode

# The pipeline will:
# 1. Open the repository webpage
# 2. Search for merged PRs containing specific commit SHAs
# 3. Install/update browser automation tools
# 4. Export all issues to JSON format
# 5. Ensure agent-browser is globally available
# 6. Fetch contributor statistics
# 7. Open result visualization
```

### Example 2: Continuous Monitoring Mode
```bash
# Run pipeline in continuous monitoring mode
./repo-analysis-pipeline --repo https://github.com/facebook/react --interval 3600

# The pipeline will complete all stages, then restart automatically
# every hour to capture repository changes and updates
```

### Example 3: Custom Output Directory
```bash
# Specify custom output location for generated files
./repo-analysis-pipeline \
  --repo https://github.com/tensorflow/tensorflow \
  --output-dir ./analysis-results \
  --format json
```

## Pipeline Stages

### Stage 1: Repository Initialization
- **Tool**: `agent-browser`
- **Command**: `agent-browser open <url>`
- **Description**: Opens the target GitHub repository webpage to initialize the analysis context. This stage establishes the baseline environment and captures initial page state.
- **Input**: Target repository URL
- **Output**: Browser session result (string)
- **Next Stage**: GitHub CLI PR search

### Stage 2: Pull Request Analysis
- **Tool**: `github-cli`
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Searches for merged pull requests containing specific commit SHAs. This stage identifies relevant PRs for further analysis and establishes commit-to-PR mappings.
- **Input**: Repository context from Stage 1
- **Output**: JSON-formatted PR data, archive files, and HTTP traces
- **Next Stage**: Browser tool maintenance

### Stage 3: Tool Maintenance
- **Tool**: `agent-browser`
- **Command**: `agent-browser install`
- **Description**: Ensures the browser automation tool is properly installed and updated. This maintenance stage guarantees reliable browser operations in subsequent stages.
- **Input**: System state from previous stages
- **Output**: Installation result (string)
- **Next Stage**: GitHub Issues export

### Stage 4: Issues Data Collection
- **Tool**: `github-cli`
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Description**: Exports comprehensive issue data including state, labels, and assignees. This stage captures the complete issue tracking history for analysis.
- **Input**: Repository and tool context
- **Output**: `issues.json` file, HTTP traces, and raw JSON responses
- **Next Stage**: Global tool setup

### Stage 5: Global Tool Configuration
- **Tool**: `agent-browser`
- **Command**: `npm install -g agent-browser`
- **Description**: Installs browser automation tools globally to ensure system-wide availability. This stage prepares the environment for distributed or repeated executions.
- **Input**: Current installation state
- **Output**: Global installation result (string)
- **Next Stage**: Contributor analysis

### Stage 6: Contributor Statistics
- **Tool**: `github-cli`
- **Command**: `gh api --paginate repos/owner/repo/contributors --jq '.[] | "\(.login): \(.contributions)"' | head -`
- **Description**: Fetches and processes contributor statistics using GitHub API. This stage analyzes contributor activity patterns and generates contribution summaries.
- **Input**: Repository data from previous stages
- **Output**: Contributor data files, HTTP traces, and formatted JSON
- **Next Stage**: Results visualization

### Stage 7: Results Presentation
- **Tool**: `agent-browser`
- **Command**: `agent-browser open <url>`
- **Description**: Opens visualization or summary pages to present analysis results. This final stage provides human-readable output and completes the analysis cycle.
- **Input**: All collected data and analysis results
- **Output**: Presentation result (string)
- **Next Stage**: Pipeline restart (Stage 1)

## Data Flow

The pipeline implements a sequential data flow where each stage's output informs the next stage's operations:

```
Repository URL
    ↓
[Stage 1: Browser Initialization]
    ↓ (session context)
[Stage 2: PR Analysis]
    ↓ (PR data + context)
[Stage 3: Tool Maintenance]
    ↓ (updated tool state)
[Stage 4: Issues Export]
    ↓ (issues data + context)
[Stage 5: Global Setup]
    ↓ (global environment)
[Stage 6: Contributor Analysis]
    ↓ (contributor data)
[Stage 7: Visualization]
    ↓ (complete analysis)
[Pipeline Restart → Stage 1]
```

## Iterative Optimization

After completing all seven stages, the pipeline automatically restarts from Stage 1. This continuous iteration allows for:
- Real-time monitoring of repository changes
- Incremental data collection and comparison
- Adaptive analysis based on previous results
- Long-term trend identification

Each iteration builds upon previous results, enabling progressive refinement of analysis and detection of patterns over time.

## Output Files

The pipeline generates several output files during execution:
- `issues.json`: Complete issue tracking data (Stage 4)
- Archive files: Compressed data collections
- HTTP traces: Full request/response logs for debugging
- JSON responses: Raw API data for programmatic processing

## Configuration Options

- `--repo`: Target repository URL (required)
- `--interval`: Restart interval in seconds (default: 3600)
- `--output-dir`: Custom output directory (default: ./output)
- `--format`: Output format [json, csv, html] (default: json)
- `--verbose`: Enable detailed logging
- `--no-restart`: Disable automatic pipeline restart

## Error Handling

The pipeline includes built-in error recovery:
- Failed stages are retried up to 3 times
- Invalid inputs trigger pipeline reset with error logging
- Network failures initiate exponential backoff retry
- Corrupted output files are regenerated from source data

## Security Notes

This pipeline requires GitHub authentication and accesses repository data. Ensure:
- Tokens have minimal required permissions
- Output files are stored securely
- Sensitive data is properly redacted
- Compliance with repository access policies

---

*Note: This tool is designed for repository analysis and monitoring purposes. Use in accordance with GitHub's Terms of Service and applicable data protection regulations.*
```