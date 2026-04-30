---
name: repo-analysis-pipeline
description: A multi-stage automated data processing pipeline for GitHub repository analysis and research. The pipeline performs authentication, repository search, and pull request analysis in a continuous cycle.
version: 1.0.0
---

# Repo Analysis Pipeline

An automated data processing pipeline designed for systematic GitHub repository analysis. The pipeline orchestrates authentication, repository research, and pull request data extraction across five sequential stages. Upon completion, the pipeline automatically restarts for continuous iterative optimization.

## Usage

The pipeline is executed as a single command. It requires a valid GitHub Personal Access Token (PAT) with appropriate scopes (`repo`, `read:org`, `read:project`) and a search topic or keyword to initiate the analysis cycle.

**Basic Command:**
```bash
./repo-analysis-pipeline --token <GITHUB_TOKEN> --topic <SEARCH_TOPIC> [--language <LANG>] [--limit <N>]
```

**Required Parameters:**
- `--token`: GitHub Personal Access Token for authentication.
- `--topic`: Primary search topic or keyword for repository discovery.

**Optional Parameters:**
- `--language`: Filter repositories by programming language (e.g., `python`, `javascript`).
- `--limit`: Maximum number of repositories to analyze per cycle (default: 50).
- `--min-stars`: Minimum star count filter for repositories.
- `--updated-within`: Timeframe filter (e.g., `30d`, `1y`).

The pipeline manages its own state and data flow between stages. Output files are saved to the `./results/` directory by default.

## Examples

**Example 1: Basic repository analysis for "machine-learning"**
```bash
./repo-analysis-pipeline --token ghp_abc123... --topic machine-learning --language python --limit 100
```
This command initiates a pipeline to find up to 100 Python repositories related to machine-learning, authenticate with GitHub, perform research, and extract associated pull request data.

**Example 2: Analysis with advanced filters**
```bash
./repo-analysis-pipeline --token ghp_xyz789... --topic blockchain --min-stars 1000 --updated-within 90d --output ./analysis_data/
```
This analyzes high-star blockchain repositories updated within the last 90 days and saves results to a custom directory.

**Example 3: Continuous monitoring mode**
```bash
./repo-analysis-pipeline --token ghp_def456... --topic cybersecurity --limit 30 --daemon
```
Runs the pipeline in daemon mode, continuously restarting the analysis cycle to monitor for new repositories and pull requests in the cybersecurity domain.

## Pipeline Stages

The pipeline consists of five sequential stages that execute automatically. Data flows from one stage to the next, with intermediate results passed as inputs to subsequent stages.

### Stage 1: Authentication & Initialization
- **Description**: `gh auth login`
- **Purpose**: Establishes authenticated session with GitHub using the provided token. Initializes the CLI environment and verifies API access permissions.
- **Key Inputs**: GitHub token, hostname configuration, output format preferences.
- **Key Outputs**: Authenticated session state, configuration files, initial API connection test results.
- **Next Stage**: Flows to **Stage 2: Repository Research (Table)**.

### Stage 2: Repository Research (Table Format)
- **Description**: `[JS CLI] node github-search.js table`
- **Purpose**: Executes targeted repository search based on the provided topic and filters. Outputs results in a structured table format for initial analysis.
- **Key Inputs**: Search topic, language filter, star count minimum, update timeframe, result limit.
- **Key Outputs**: JSON file (`/tmp/gh_results.json` or `results/${safe_topic}.json`) containing repository metadata in tabular structure.
- **Next Stage**: Flows to **Stage 3: Pull Request Analysis**.

### Stage 3: Pull Request Analysis
- **Description**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Purpose**: Analyzes pull requests from repositories identified in Stage 2. Focuses on merged PRs to understand code integration patterns and project activity.
- **Key Inputs**: Repository identifiers from previous stage, search queries, state filters, output field specifications.
- **Key Outputs**: JSON data containing PR numbers, titles, and URLs; HTTP request/response details for debugging.
- **Next Stage**: Flows to **Stage 4: Repository Research (CSV Format)**.

### Stage 4: Repository Research (CSV Format)
- **Description**: `[JS CLI] node github-search.js csv`
- **Purpose**: Performs additional repository research with refined parameters, outputting results in CSV-compatible format for further data processing.
- **Key Inputs**: Refined search parameters based on previous stages' findings, output format specification.
- **Key Outputs**: JSON files formatted for CSV conversion (`/tmp/gh_results.json` and `results/${safe_topic}.json`).
- **Next Stage**: Flows to **Stage 5: Session Renewal**.

### Stage 5: Session Renewal
- **Description**: `gh auth login`
- **Purpose**: Renews authentication session and prepares the pipeline for the next iteration cycle. Ensures continuous operation without manual reauthentication.
- **Key Inputs**: Session refresh parameters, token validation flags.
- **Key Outputs**: Updated authentication state, session tokens, configuration verification.
- **Next Stage**: Returns to **Stage 1** to begin the next analysis iteration.

## Data Flow & Iteration

The pipeline implements a circular data flow pattern:
1. Stages execute sequentially from 1 to 5
2. Output from each stage becomes input for the next
3. After Stage 5 completes, the pipeline automatically restarts at Stage 1
4. Each iteration incorporates learnings from previous cycles for refined analysis

This design enables continuous monitoring and iterative optimization of repository analysis parameters based on historical results and emerging patterns.

## Output Files

- `results/{topic}_table.json`: Tabular repository data from Stage 2
- `results/{topic}_pr_analysis.json`: Pull request analysis from Stage 3
- `results/{topic}_csv_data.json`: CSV-formatted repository data from Stage 4
- `pipeline_state.log`: Execution log with timestamps and stage transitions
- `auth_session.json`: Current authentication state (encrypted)

## Notes

- Ensure the GitHub token has sufficient permissions for the intended analysis scope.
- The pipeline creates and manages temporary files in `/tmp/` and the `./results/` directory.
- For long-running operations, consider implementing rate limit handling and error recovery mechanisms.
- This tool is designed for research and data analysis purposes only.