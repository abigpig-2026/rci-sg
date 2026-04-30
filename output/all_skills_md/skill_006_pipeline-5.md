```yaml
---
name: repo-analysis-pipeline
description: A multi-stage automated data processing pipeline for repository analysis and monitoring. It orchestrates browser automation and GitHub CLI operations to collect and process repository metadata in a continuous cycle.
version: 1.0.0
---

# Repo Analysis Pipeline

## Overview

The Repo Analysis Pipeline is an automated data processing workflow designed to collect, analyze, and monitor repository metadata from web sources and GitHub. It operates as a sequential, multi-stage pipeline where the output of one stage automatically becomes the input for the next. Upon completion of all stages, the pipeline resets and begins a new iteration for continuous monitoring and optimization.

## Usage

To execute the pipeline, invoke the primary command. The pipeline will run autonomously through its defined stages.

```bash
# Start the pipeline
repo-analysis-pipeline
```

The pipeline requires the following environment setup:
- A configured `agent-browser` tool with network access.
- GitHub CLI (`gh`) installed and authenticated.
- Sufficient permissions to list PRs and issues on the target repositories.

## Examples

### Basic Execution
Run the complete pipeline cycle once.

```bash
repo-analysis-pipeline --run-once
```

### Continuous Monitoring
Run the pipeline in a loop with a specified interval between iterations.

```bash
repo-analysis-pipeline --interval 300  # Runs every 5 minutes
```

### Targeted Analysis
Provide a specific repository and commit SHA for the pipeline to analyze.

```bash
repo-analysis-pipeline --repo owner/repo-name --sha abc123def
```

## Pipeline Stages

The pipeline consists of five sequential stages. Data flows automatically from one stage to the next.

### Stage 1: Initial Web Data Fetch
- **Tool:** `agent-browser`
- **Command:** `agent-browser open https://example.com`
- **Description:** Opens a target URL to fetch initial web data or configuration. This stage serves as the entry point, often retrieving a SHA, repository identifier, or other seed data required for subsequent GitHub queries.
- **Input:** Accepts various parameters including `url`, `json`, `text`, and session management flags.
- **Output:** A `result` string containing the fetched data (e.g., a commit SHA).
- **Next Stage:** Output is passed to Stage 2 (`github-cli`).

### Stage 2: Merged PR Lookup
- **Tool:** `github-cli`
- **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description:** Queries the GitHub repository for Pull Requests that have been merged and contain the SHA obtained from Stage 1. This identifies which PR introduced a specific change.
- **Input:** Uses the `result` string from Stage 1 as the `SHA_HERE` value in the search query. Accepts numerous `gh` CLI flags for filtering and output formatting, notably `--json`.
- **Output:** JSON data containing PR numbers, titles, and URLs. May also output files or raw HTTP logs.
- **Next Stage:** The JSON output is passed to Stage 3 (`agent-browser`).

### Stage 3: Dependency Preparation
- **Tool:** `agent-browser`
- **Command:** `agent-browser install --with-deps`
- **Description:** Prepares the environment for further processing. On Linux systems, this installs necessary system dependencies. This stage ensures the runtime environment is configured for any subsequent data handling or analysis steps.
- **Input:** Can receive the JSON output from Stage 2. Uses the `--with-deps` flag for comprehensive installation.
- **Output:** A `result` string indicating installation success or status.
- **Next Stage:** Output is passed to Stage 4 (`github-cli`).

### Stage 4: Comprehensive Issue Export
- **Tool:** `github-cli`
- **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Description:** Exports a comprehensive snapshot of all repository issues (open and closed) to a local JSON file. This creates a dataset for trend analysis, backlog review, or reporting.
- **Input:** Can utilize the status from Stage 3. Uses flags like `--state all`, `--limit`, and `--json` to control the export.
- **Output:** A file named `issues.json` containing detailed issue metadata. May also produce auxiliary output.
- **Next Stage:** Control and the generated file path are passed to Stage 5 (`agent-browser`).

### Stage 5: Results Verification & Continuation
- **Tool:** `agent-browser`
- **Command:** `agent-browser open https://example.com`
- **Description:** Opens a final URL, which could be a dashboard, a report page, or a webhook endpoint to signal pipeline completion. This stage acts as a verification step and the trigger to restart the pipeline cycle.
- **Input:** Receives the pipeline's final state and outputs.
- **Output:** A `result` string confirming the action.
- **Next Stage:** The pipeline logic resets, and execution loops back to **Stage 1** to begin the next analysis iteration.

## Data Flow Diagram

```
[Stage 1: agent-browser]
        |
        v (SHA/Data)
[Stage 2: github-cli]
        |
        v (PR JSON)
[Stage 3: agent-browser]
        |
        v (Status)
[Stage 4: github-cli]
        |
        v (issues.json file)
[Stage 5: agent-browser]
        |
        v (Completion Signal)
        |
[Loop Back to Stage 1]
```

## Notes

- This pipeline is designed for automated, periodic repository analysis.
- Ensure proper authentication and rate limit management for the GitHub API.
- The example URLs (`https://example.com`) should be replaced with actual target endpoints in a production configuration.
- The pipeline's iterative nature allows it to detect changes (new PRs, issues) across successive runs.
```