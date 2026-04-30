```yaml
---
name: repo-workflow-analyzer
description: A multi-stage automated pipeline for GitHub repository workflow analysis and data processing
version: 1.0.0
---

# Repo Workflow Analyzer

An automated data processing pipeline designed to analyze GitHub repository workflows, issues, and pull requests through a sequential multi-stage process. The pipeline executes a series of GitHub CLI operations, processes the results, and automatically flows between stages to provide comprehensive repository insights.

## Usage

To use the Repo Workflow Analyzer pipeline, ensure you have the GitHub CLI (`gh`) installed and authenticated. The pipeline runs automatically through its seven stages, with each stage's output feeding into the next.

```bash
# Initialize the pipeline (starts Stage 1)
./repo-workflow-analyzer --start
```

### Configuration Options

- `--repo <owner/repo>`: Specify the target repository (required)
- `--output-format <json|text>`: Set output format (default: text)
- `--run-id <id>`: Specify workflow run ID for Stage 6
- `--sha <commit-sha>`: Specify commit SHA for Stage 3 search

## Examples

### Basic Repository Analysis

```bash
./repo-workflow-analyzer --repo octocat/Hello-World --output-format json
```

This command analyzes the octocat/Hello-World repository, producing JSON-formatted output with issue lists, PR information, and workflow run details.

### Targeted PR Search Analysis

```bash
./repo-workflow-analyzer --repo microsoft/vscode --sha abc123def456 --run-id 123456789
```

Analyzes the vscode repository, searching for PRs containing the specified commit SHA and examining a specific workflow run.

### Complete Pipeline with Custom Output

```bash
./repo-workflow-analyzer --repo facebook/react --output-format text > analysis-report.txt
```

Runs the full seven-stage pipeline on the React repository and saves the formatted analysis to a text file.

## Pipeline Stages

The pipeline consists of seven sequential stages that execute automatically. Each stage completes its processing before flowing to the next stage.

### Stage 1: Authentication Initialization
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh auth login`
- **Description**: Initializes authentication and prepares the environment for GitHub operations. This stage ensures proper credentials are available for subsequent API calls.
- **Inputs**: Authentication parameters, token configuration, hostname settings
- **Outputs**: Authentication status, token validation, configuration files
- **Next Stage**: Flows to Stage 2 (GitHub Issue Listing)

### Stage 2: Issue Listing and Formatting
- **Tool**: GitHub (`gh`)
- **Command**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Description**: Retrieves and formats repository issues into a readable list. Extracts issue numbers and titles, applying jq filtering for clean output.
- **Inputs**: Repository specification, JSON formatting options, jq filter
- **Outputs**: Formatted issue list as string output
- **Next Stage**: Flows to Stage 3 (PR Search)

### Stage 3: Pull Request Search by SHA
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Searches for pull requests containing a specific commit SHA that have been merged. Returns PR metadata including numbers, titles, and URLs.
- **Inputs**: SHA search parameter, state filter (merged), JSON output fields
- **Outputs**: JSON array of matching pull requests with metadata
- **Next Stage**: Flows to Stage 4 (PR Detail Retrieval)

### Stage 4: Pull Request Detail Extraction
- **Tool**: GitHub (`gh`)
- **Command**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **Description**: Retrieves detailed information about a specific pull request (PR #55 in example). Extracts key fields including title, state, and author.
- **Inputs**: API endpoint path, jq extraction filter
- **Outputs**: Formatted string with PR title, state, and author username
- **Next Stage**: Flows to Stage 5 (Comprehensive Issue Export)

### Stage 5: Complete Issue Data Export
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Description**: Exports comprehensive issue data including all states, with extended metadata (labels, assignees). Outputs to JSON file for further processing.
- **Inputs**: State filter (all), high limit count, extensive JSON field selection
- **Outputs**: JSON file containing complete issue dataset
- **Next Stage**: Flows to Stage 6 (Workflow Run Inspection)

### Stage 6: Workflow Run Analysis
- **Tool**: GitHub (`gh`)
- **Command**: `gh run view <run-id> --repo owner/repo`
- **Description**: Inspects a specific GitHub Actions workflow run, displaying execution details, status, and results.
- **Inputs**: Workflow run ID, repository specification
- **Outputs**: Detailed workflow run information as formatted string
- **Next Stage**: Flows to Stage 7 (Authentication Refresh)

### Stage 7: Authentication Refresh
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh auth login`
- **Description**: Refreshes authentication credentials to ensure continued API access. This stage completes the pipeline cycle and prepares for the next iteration.
- **Inputs**: Authentication refresh parameters
- **Outputs**: Updated authentication status
- **Next Stage**: Returns to Stage 1 (pipeline restarts for next iteration)

## Data Flow

The pipeline implements a unidirectional data flow where each stage's output becomes the context for the next stage:

1. **Stage 1** → Authentication context → **Stage 2**
2. **Stage 2** → Issue list data → **Stage 3**
3. **Stage 3** → PR search results → **Stage 4**
4. **Stage 4** → PR detail information → **Stage 5**
5. **Stage 5** → Complete issue dataset → **Stage 6**
6. **Stage 6** → Workflow run analysis → **Stage 7**
7. **Stage 7** → Refreshed auth context → **Stage 1** (next iteration)

This cyclical flow allows for continuous repository monitoring and analysis, with each iteration building upon previous results.

## Output Formats

The pipeline supports multiple output formats:

- **Text**: Human-readable formatted output (default)
- **JSON**: Structured JSON for programmatic processing
- **File**: Direct file output for specific stages (e.g., issues.json)

## Requirements

- GitHub CLI (`gh`) version 2.0.0 or higher
- Valid GitHub authentication (token or OAuth)
- Network access to GitHub API endpoints
- Sufficient repository permissions for read operations

## Notes

- The pipeline is designed for repository analysis and monitoring purposes
- All GitHub API rate limits apply to pipeline operations
- Authentication tokens must have appropriate repository access permissions
- The pipeline can be scheduled for periodic execution (e.g., daily analysis)
- Output files are overwritten on each pipeline execution

---

*This tool is intended for repository analysis, monitoring, and workflow optimization purposes.*
```