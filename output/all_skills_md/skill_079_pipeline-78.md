```yaml
---
name: repo-workflow-analyzer
description: A multi-stage automated data processing pipeline for GitHub repository workflow analysis. The pipeline collects and processes repository metadata, issues, pull requests, and workflow runs in sequential stages, then restarts for continuous monitoring.
version: 1.0.0
---

# Repo Workflow Analyzer

An automated data processing pipeline that performs sequential analysis of GitHub repository workflows. The pipeline executes a series of GitHub CLI commands to collect repository metadata, track issues and pull requests, and monitor workflow runs. Each stage processes data and passes results to the next stage, creating a continuous analysis loop for repository monitoring and optimization.

## Usage

To execute the pipeline, ensure you have the GitHub CLI (`gh`) installed and authenticated. The pipeline runs automatically through all stages in sequence.

```bash
# Start the pipeline execution
./repo-workflow-analyzer start --repo owner/repository-name
```

### Configuration Options

- `--repo`: Target repository in format `owner/repo` (required)
- `--interval`: Time between pipeline iterations in minutes (default: 60)
- `--output-dir`: Directory for pipeline results (default: ./analysis-results)
- `--verbose`: Enable detailed logging of each stage

## Examples

### Basic Repository Analysis
```bash
./repo-workflow-analyzer start --repo octocat/Hello-World
```

### Continuous Monitoring with Custom Interval
```bash
./repo-workflow-analyzer start --repo microsoft/vscode --interval 30 --output-dir /data/vscode-analysis
```

### One-time Analysis Run
```bash
./repo-workflow-analyzer run-once --repo google/googletest --verbose
```

## Pipeline Stages

The pipeline consists of 7 sequential stages that execute in order. After completion, the pipeline restarts from stage 1 for continuous monitoring.

### Stage 1: Authentication Initialization
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh auth login`
- **Purpose**: Establishes authenticated session with GitHub API
- **Input**: Authentication parameters and configuration flags
- **Output**: Authentication token and session data
- **Next Stage**: Stage 2 (Repository Issue Listing)

### Stage 2: Issue Summary Extraction
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Purpose**: Extracts formatted list of repository issues
- **Input**: Repository specification and output formatting parameters
- **Output**: Formatted string of issue numbers and titles
- **Next Stage**: Stage 3 (Pull Request Search)

### Stage 3: Pull Request Analysis
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Purpose**: Searches for merged pull requests containing specific commit SHA
- **Input**: Search criteria, state filters, and output format parameters
- **Output**: JSON data of matching pull requests
- **Next Stage**: Stage 4 (Pull Request Detail Fetch)

### Stage 4: Pull Request Detail Retrieval
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **Purpose**: Fetches detailed information for specific pull request #55
- **Input**: API endpoint path and JQ query for data extraction
- **Output**: Formatted pull request details (title, state, author)
- **Next Stage**: Stage 5 (Comprehensive Issue Export)

### Stage 5: Complete Issue Data Export
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Purpose**: Exports comprehensive issue data to JSON file
- **Input**: State filters, pagination limits, and field selection
- **Output**: JSON file containing complete issue dataset
- **Next Stage**: Stage 6 (Workflow Run Listing)

### Stage 6: Workflow Run Monitoring
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh run list --repo owner/repo --limit 10`
- **Purpose**: Lists recent workflow runs for the repository
- **Input**: Repository specification and result limit
- **Output**: List of recent workflow runs with status information
- **Next Stage**: Stage 7 (Session Refresh)

### Stage 7: Authentication Refresh
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh auth login`
- **Purpose**: Refreshes authentication token for next pipeline iteration
- **Input**: Authentication parameters (same as Stage 1)
- **Output**: Updated authentication session
- **Next Stage**: Stage 1 (Pipeline restart for next iteration)

## Data Flow

The pipeline implements a unidirectional data flow where each stage's output informs the next stage's execution:

1. **Authentication** → **Issue Summary** → **PR Search** → **PR Details** → **Issue Export** → **Workflow Runs** → **Auth Refresh**
2. After Stage 7 completes, the pipeline automatically restarts at Stage 1
3. Each iteration builds upon previous data, enabling trend analysis over time
4. Critical data points are persisted between iterations for continuity

## Output Files

The pipeline generates the following output files in the specified output directory:

- `issues.json`: Complete issue dataset from Stage 5
- `pipeline-log-{timestamp}.txt`: Execution log for each pipeline run
- `analysis-summary-{timestamp}.md`: Markdown summary of findings
- `auth-session-{timestamp}.bin`: Serialized authentication session

## Requirements

- GitHub CLI (`gh`) version 2.0.0 or higher
- Valid GitHub account with repository access
- Network connectivity to GitHub API endpoints
- Sufficient storage for analysis results

## Notes

- The pipeline is designed for automated, continuous repository monitoring
- Each stage validates its inputs before execution
- Authentication tokens are securely managed and refreshed as needed
- Pipeline execution can be paused/resumed without data loss
- All API calls respect GitHub rate limits with automatic backoff

---

*This tool is intended for repository analysis and workflow optimization purposes. Ensure you have appropriate permissions for target repositories.*