```yaml
---
name: repo-workflow-analyzer
description: A multi-stage automated data processing pipeline for GitHub repository workflow analysis and monitoring.
version: 1.0.0
---

# Repo Workflow Analyzer

An automated data processing pipeline designed to collect, analyze, and monitor GitHub repository workflow data across multiple stages. The pipeline sequentially executes a series of GitHub CLI and API operations, automatically passing data between stages to provide comprehensive repository insights. Upon completion of all stages, the pipeline can be configured to restart for continuous monitoring and iterative optimization.

## Usage

The pipeline is executed as a single unit. Configure the target repository and authentication details before initiation.

**Prerequisites:**
- GitHub CLI (`gh`) installed and configured
- Valid GitHub authentication token with appropriate repository permissions
- Target repository in `owner/repo` format

**Basic Execution:**
```bash
# Set target repository environment variable
export TARGET_REPO="owner/repo"

# Execute the complete pipeline
./repo-workflow-analyzer --repo $TARGET_REPO
```

**Configuration Options:**
- `--repo`: Specify the target repository (required)
- `--output-dir`: Directory for pipeline output files (default: ./output)
- `--interval`: Minutes between pipeline iterations for continuous mode (default: 60)
- `--single-run`: Execute pipeline once and exit (default: false)

## Examples

**Example 1: Basic repository analysis**
```bash
./repo-workflow-analyzer --repo octocat/Hello-World --output-dir ./reports
```

**Example 2: Continuous monitoring with custom interval**
```bash
./repo-workflow-analyzer --repo microsoft/vscode --interval 30
```

**Example 3: Single execution with detailed logging**
```bash
./repo-workflow-analyzer --repo facebook/react --single-run --verbose
```

**Expected Output Structure:**
```
output/
├── issues_summary.txt          # Stage 2 output
├── pr_search_results.json      # Stage 3 intermediate data
├── pull_request_details.txt    # Stage 4 output
├── issues_complete.json        # Stage 5 output
└── workflow_runs.txt           # Stage 6 output
```

## Pipeline Stages

The pipeline consists of 7 sequential stages that execute automatically. Each stage's output serves as input or context for subsequent stages.

### Stage 1: Authentication Initialization
- **Tool**: GitHub CLI (`github-cli`)
- **Command**: `gh auth login`
- **Purpose**: Establishes authenticated session for subsequent GitHub operations
- **Input**: Authentication credentials and configuration parameters
- **Output**: Authenticated session token and configuration files
- **Next Stage**: Automatically proceeds to Stage 2 upon successful authentication

### Stage 2: Issue Listing and Summary
- **Tool**: GitHub (`github`)
- **Command**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Purpose**: Retrieves and formats a concise list of repository issues
- **Input**: Repository specification and output formatting parameters
- **Output**: Formatted string containing issue numbers and titles
- **Next Stage**: Automatically proceeds to Stage 3

### Stage 3: Pull Request Search by Commit
- **Tool**: GitHub CLI (`github-cli`)
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Purpose**: Searches for pull requests associated with specific commit SHAs
- **Input**: Search criteria, state filters, and output format specifications
- **Output**: JSON data containing matching pull request details
- **Next Stage**: Automatically proceeds to Stage 4

### Stage 4: Pull Request Detail Extraction
- **Tool**: GitHub (`github`)
- **Command**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **Purpose**: Extracts detailed information about specific pull requests
- **Input**: API endpoint path and data extraction queries
- **Output**: Formatted string with pull request metadata
- **Next Stage**: Automatically proceeds to Stage 5

### Stage 5: Comprehensive Issue Export
- **Tool**: GitHub CLI (`github-cli`)
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Purpose**: Exports complete issue data for analysis and archiving
- **Input**: Comprehensive filtering and formatting parameters
- **Output**: JSON file containing complete issue dataset
- **Next Stage**: Automatically proceeds to Stage 6

### Stage 6: Workflow Run Listing
- **Tool**: GitHub (`github`)
- **Command**: `gh run list --repo owner/repo --limit 10`
- **Purpose**: Lists recent workflow runs for repository activity monitoring
- **Input**: Repository specification and result limiting parameters
- **Output**: Formatted list of recent workflow executions
- **Next Stage**: Automatically proceeds to Stage 7

### Stage 7: Session Renewal
- **Tool**: GitHub CLI (`github-cli`)
- **Command**: `gh auth login`
- **Purpose**: Renews authentication session for continuous operation
- **Input**: Authentication parameters (reuses Stage 1 configuration)
- **Output**: Refreshed authentication tokens and session data
- **Next Stage**: Returns to Stage 1 to begin next iteration (if in continuous mode)

## Data Flow

The pipeline implements a linear data flow where each stage's output informs subsequent operations:

1. **Authentication** → **Issue Summary** → **PR Search** → **PR Details** → **Issue Export** → **Workflow List** → **Authentication Renewal**

2. Between iterations, aggregated data is compiled into comprehensive reports in the specified output directory.

3. The pipeline maintains state between iterations, allowing for delta analysis and trend identification in continuous operation mode.

## Output Files

The pipeline generates the following output files in the specified directory:

1. `issues_summary.txt` - Human-readable issue list from Stage 2
2. `pr_search_results.json` - JSON data from Stage 3 PR searches
3. `pull_request_details.txt` - Detailed PR information from Stage 4
4. `issues_complete.json` - Complete issue dataset from Stage 5
5. `workflow_runs.txt` - Recent workflow execution list from Stage 6
6. `pipeline_summary_report.md` - Aggregated analysis compiled after each complete iteration

## Configuration

Create a `config.yaml` file in the execution directory to customize pipeline behavior:

```yaml
repository: "owner/repo"
output_directory: "./analysis_results"
continuous_mode: true
iteration_interval_minutes: 60
data_retention_days: 30
log_level: "info"
```

## Notes

- The pipeline requires stable network connectivity for GitHub API access
- Authentication tokens must have appropriate scopes for all operations
- Large repositories may require adjusted rate limiting in configuration
- Output files are overwritten with each pipeline iteration
- For continuous operation, ensure proper process management and logging

---
*This tool is designed for repository analysis and workflow monitoring purposes.*
```