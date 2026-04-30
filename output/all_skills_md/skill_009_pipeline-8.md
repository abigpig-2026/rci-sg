```yaml
---
name: repo-analysis-pipeline
description: |
  A multi-stage automated data processing pipeline for repository analysis.
  This pipeline orchestrates browser automation and GitHub CLI operations
  to collect, process, and analyze repository data in a continuous cycle.
version: 1.0.0
---

# Repo Analysis Pipeline

An automated data processing pipeline that performs repository analysis through coordinated browser automation and GitHub operations. The pipeline executes seven sequential stages, automatically passing data between stages, and restarts upon completion for continuous iterative optimization.

## Usage

To execute the pipeline, run the main pipeline command with appropriate parameters:

```bash
repo-analysis-pipeline --target-url <URL> --repo <owner/repo> [--output-dir <path>]
```

**Parameters:**
- `--target-url`: The initial URL to open in the browser (default: https://example.com)
- `--repo`: Target repository in `owner/repo` format (required)
- `--output-dir`: Directory for output files (default: ./output)
- `--iterations`: Number of pipeline cycles to run (default: 1)

**Environment Variables:**
- `GITHUB_TOKEN`: GitHub authentication token (required for GitHub CLI operations)
- `BROWSER_PATH`: Custom browser executable path (optional)

## Examples

### Basic Repository Analysis
```bash
export GITHUB_TOKEN="ghp_your_token_here"
repo-analysis-pipeline --repo "octocat/Hello-World" --target-url "https://github.com"
```

### Multiple Iterations with Custom Output
```bash
repo-analysis-pipeline \
  --repo "microsoft/vscode" \
  --output-dir "/data/analysis" \
  --iterations 3
```

### Pipeline with Debug Output
```bash
repo-analysis-pipeline --repo "torvalds/linux" --verbose
```

## Pipeline Stages

The pipeline consists of seven sequential stages that execute automatically. Each stage's output becomes the next stage's input, creating a continuous data flow.

### Stage 1: Initial Browser Session
- **Tool**: agent-browser
- **Command**: `agent-browser open https://example.com`
- **Purpose**: Initializes browser session and navigates to target URL
- **Input**: URL parameter or default target
- **Output**: Browser session state and page content
- **Next Stage**: Stage 2 (GitHub CLI)

### Stage 2: Pull Request Search
- **Tool**: github-cli
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Purpose**: Searches for merged pull requests containing specific commit SHA
- **Input**: SHA extracted from previous stage or pipeline context
- **Output**: JSON array of PR data (number, title, URL)
- **Next Stage**: Stage 3 (agent-browser)

### Stage 3: Dependency Installation
- **Tool**: agent-browser
- **Command**: `agent-browser install --with-deps`
- **Purpose**: Installs required system dependencies for browser automation
- **Input**: System requirements from previous analysis
- **Output**: Installation status and dependency tree
- **Next Stage**: Stage 4 (GitHub CLI)

### Stage 4: Issue Collection
- **Tool**: github-cli
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Purpose**: Collects comprehensive issue data from repository
- **Input**: Repository context from previous stages
- **Output**: issues.json file containing all repository issues
- **Next Stage**: Stage 5 (agent-browser)

### Stage 5: Browser Runtime Setup
- **Tool**: agent-browser
- **Command**: `agent-browser install`
- **Purpose**: Downloads and configures Chromium browser runtime
- **Input**: Installation requirements from previous stage
- **Output**: Browser binary and runtime configuration
- **Next Stage**: Stage 6 (GitHub CLI)

### Stage 6: Contributor Analysis
- **Tool**: github-cli
- **Command**: `gh api --paginate repos/owner/repo/contributors --jq '.[] | "\(.login): \(.contributions)"' | head -`
- **Purpose**: Analyzes repository contributors and their contribution counts
- **Input**: Repository owner/name from pipeline parameters
- **Output**: Formatted contributor list with contribution statistics
- **Next Stage**: Stage 7 (agent-browser)

### Stage 7: Final Browser Validation
- **Tool**: agent-browser
- **Command**: `agent-browser open https://example.com`
- **Purpose**: Validates browser functionality and session persistence
- **Input**: Session state from previous browser operations
- **Output**: Final validation result and session summary
- **Next Stage**: Pipeline restart (Stage 1)

## Data Flow

The pipeline implements a unidirectional data flow where each stage processes data and passes it to the next:

```
Stage 1 (Browser Init) → Stage 2 (PR Search) → Stage 3 (Deps Install)
→ Stage 4 (Issue Collect) → Stage 5 (Browser Setup) → Stage 6 (Contributor Analysis)
→ Stage 7 (Validation) → [Pipeline Restart]
```

**Data Types Handled:**
- JSON structures (PR data, issue data, contributor data)
- Browser session states
- File outputs (issues.json, configuration files)
- System dependency information

## Output Files

The pipeline generates the following output files in the specified output directory:

1. `issues.json` - Complete issue data from Stage 4
2. `pipeline.log` - Execution log with timestamps
3. `contributors.txt` - Contributor analysis from Stage 6
4. `session_summary.json` - Browser session metadata

## Error Handling

The pipeline includes robust error handling:
- Stage failures trigger pipeline restart with error logging
- Missing dependencies prompt automatic installation attempts
- GitHub API rate limits trigger exponential backoff
- Browser crashes initiate session recovery procedures

## Security Notes

This pipeline requires:
- GitHub token with `repo` scope for private repositories
- Network access for browser automation and API calls
- Local filesystem access for output generation

All operations are logged and no sensitive data is persisted beyond the execution session.

---

*Note: This pipeline is designed for automated repository analysis and monitoring. Ensure you have appropriate permissions before analyzing private repositories.*