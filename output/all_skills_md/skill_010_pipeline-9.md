---
name: repo-snapshot-pipeline
description: |
  A multi-stage automated data processing pipeline for collecting and analyzing GitHub repository metadata.
  The pipeline orchestrates browser automation and GitHub CLI operations to gather comprehensive repository information,
  then cycles back to the beginning for continuous monitoring and optimization.
version: 1.0.0
---

# Repo Snapshot Pipeline

An automated, multi-stage data processing pipeline designed to systematically collect, process, and analyze GitHub repository metadata. The pipeline coordinates between browser automation and GitHub CLI commands to gather data on pull requests, issues, starred repositories, and perform environment setup. Each stage's output automatically flows into the next, and upon completion, the pipeline resets for the next iteration of data collection and optimization.

## Usage

To execute the complete pipeline, run the primary pipeline command. The pipeline will automatically progress through all seven stages in sequence.

```bash
# Execute the full pipeline cycle
run-repo-snapshot-pipeline
```

The pipeline manages its own state and data flow. No manual intervention is required between stages.

## Examples

### Basic Execution
Run a single, complete iteration of the pipeline to collect a snapshot of repository data.

```bash
run-repo-snapshot-pipeline
```
*Output: A consolidated report summarizing the collected PRs, issues, starred repos, and setup status.*

### Pipeline Status Check
Check the current status and progress of a running pipeline instance.

```bash
run-repo-snapshot-pipeline --status
```

### Custom Target URL
Override the default target URL for the browser stages (Stages 1 & 7).

```bash
run-repo-snapshot-pipeline --target-url "https://github.com/your-org"
```

## Pipeline Stages

The pipeline consists of seven sequential stages. Data flows automatically from one stage to the next.

### Stage 1: Initial Browser Session
*Agent: `agent-browser`*
- **Description**: Opens the initial target URL (`https://example.com` by default) to establish a browser session and context for subsequent operations.
- **Primary Action**: `agent-browser open <target-url>`
- **Inputs**: URL, session parameters, JSON/text payload options.
- **Output**: Browser session result (string).
- **Next Stage**: Automatically flows to Stage 2 (GitHub CLI).

### Stage 2: Merged PR Search
*Agent: `github-cli`*
- **Description**: Searches for merged pull requests associated with a specific commit SHA (placeholder `SHA_HERE`). Extracts key metadata (PR number, title, URL) in JSON format.
- **Primary Action**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Inputs**: GitHub CLI flags for search, state filtering, and JSON output.
- **Output**: JSON array of merged PR data, or a structured file/URL response.
- **Next Stage**: Automatically flows to Stage 3 (agent-browser).

### Stage 3: Environment Setup (with Dependencies)
*Agent: `agent-browser`*
- **Description**: Performs an installation routine, including system dependencies (simulated Linux environment setup). Prepares the environment for data collection tasks.
- **Primary Action**: `agent-browser install --with-deps`
- **Inputs**: Installation flags, dependency options.
- **Output**: Installation result and status (string).
- **Next Stage**: Automatically flows to Stage 4 (GitHub CLI).

### Stage 4: Issue Inventory Export
*Agent: `github-cli`*
- **Description**: Lists all issues (open and closed) from the target repository, with a high limit (9999). Exports comprehensive metadata (number, title, state, labels, assignees) to a JSON file (`issues.json`).
- **Primary Action**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Inputs**: GitHub CLI flags for state, limit, JSON field selection, and output redirection.
- **Output**: File (`issues.json`) containing the issue dataset.
- **Next Stage**: Automatically flows to Stage 5 (agent-browser).

### Stage 5: Browser Runtime Setup
*Agent: `agent-browser`*
- **Description**: Downloads and installs the Chromium browser runtime required for headless browser automation in later stages.
- **Primary Action**: `agent-browser install`
- **Inputs**: Installation command.
- **Output**: Installation result and status (string).
- **Next Stage**: Automatically flows to Stage 6 (GitHub CLI).

### Stage 6: Starred Repos Sampling
*Agent: `github-cli`*
- **Description**: Calls the GitHub API to fetch the list of repositories starred by the authenticated user. Uses pagination and `jq` to extract full names, then samples the first 20 entries.
- **Primary Action**: `gh api --paginate user/starred --jq '.[].full_name' | head -20`
- **Inputs**: GitHub API command with pagination, JQ filter, and shell pipe.
- **Output**: List of up to 20 repository full names (JSON/text).
- **Next Stage**: Automatically flows to Stage 7 (agent-browser).

### Stage 7: Final Verification & Reset
*Agent: `agent-browser`*
- **Description**: Opens the target URL again to verify connectivity and session state. This stage completes the data collection cycle and signals the pipeline to reset for the next iteration.
- **Primary Action**: `agent-browser open https://example.com`
- **Inputs**: URL, session parameters.
- **Output**: Final session result (string).
- **Next Stage**: Pipeline completes and automatically resets to Stage 1 for the next optimization cycle.

---
*Note: This tool is designed for automated data aggregation and analysis workflows. Ensure compliance with GitHub's Terms of Service and API rate limits when operating this pipeline.*