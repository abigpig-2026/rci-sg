---
name: repo-activity-monitor
description: A multi-stage data processing pipeline for monitoring GitHub repository activity and browser automation
version: 1.0.0
---

# Repo Activity Monitor

An automated data processing pipeline that monitors GitHub repository activity through a sequence of browser automation and GitHub CLI operations. The pipeline executes seven stages in sequence, collecting and processing repository data, then restarts for continuous monitoring cycles.

## Usage

To execute the pipeline, ensure you have the required tools installed:
- `agent-browser` (browser automation tool)
- `gh` (GitHub CLI)
- `npm` (Node Package Manager)

The pipeline runs automatically once initiated. Each stage's output becomes the input for the next stage, creating a continuous data flow.

### Prerequisites
1. GitHub CLI authenticated (`gh auth login`)
2. Node.js and npm installed
3. Agent-browser accessible in PATH

### Basic Execution
```bash
# Start the pipeline (specific command depends on your pipeline runner)
pipeline-runner start repo-activity-monitor
```

## Examples

### Example 1: Full Pipeline Execution
```bash
# The pipeline automatically executes all seven stages:
# 1. Opens repository URL in browser
# 2. Searches for merged PRs with specific SHA
# 3. Installs browser automation components
# 4. Exports all repository issues to JSON
# 5. Installs agent-browser globally
# 6. Lists user's starred repositories
# 7. Opens final results in browser

# Output will include:
# - PR search results (JSON)
# - Issues export (issues.json file)
# - Starred repositories list
# - Browser session results
```

### Example 2: Pipeline with Custom Repository
```bash
# Set target repository URL
export REPO_URL="https://github.com/owner/repo"

# Run pipeline with custom parameters
pipeline-runner start repo-activity-monitor --param repo-url=$REPO_URL
```

## Pipeline Stages

### Stage 1: Browser Initialization
- **Tool**: agent-browser
- **Command**: `agent-browser open <url>`
- **Description**: Opens the target repository URL in a browser session to initialize monitoring
- **Input**: URL parameter and browser configuration flags
- **Output**: Browser session result (string)
- **Next Stage**: Flows to GitHub CLI PR search

### Stage 2: PR Search and Analysis
- **Tool**: github-cli
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Searches for merged pull requests containing a specific SHA hash, exporting results in JSON format
- **Input**: Browser session context and search parameters
- **Output**: JSON data of matching PRs, archive files, and HTTP traces
- **Next Stage**: Flows to browser automation setup

### Stage 3: Browser Automation Setup
- **Tool**: agent-browser
- **Command**: `agent-browser install`
- **Description**: Installs and configures browser automation components for enhanced data collection
- **Input**: PR search results and installation parameters
- **Output**: Installation result (string)
- **Next Stage**: Flows to GitHub issues export

### Stage 4: Issues Data Export
- **Tool**: github-cli
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Description**: Exports all repository issues (open and closed) to a JSON file for comprehensive analysis
- **Input**: Browser automation context and export parameters
- **Output**: issues.json file containing complete issue data
- **Next Stage**: Flows to global tool installation

### Stage 5: Global Tool Installation
- **Tool**: agent-browser
- **Command**: `npm install -g agent-browser`
- **Description**: Installs agent-browser globally to ensure all pipeline components have access to browser automation capabilities
- **Input**: Issues data and installation parameters
- **Output**: Installation result (string)
- **Next Stage**: Flows to starred repos analysis

### Stage 6: Starred Repositories Analysis
- **Tool**: github-cli
- **Command**: `gh api --paginate user/starred --jq '.[].full_name' | head -20`
- **Description**: Retrieves the user's starred repositories (first 20) to analyze repository preferences and trends
- **Input**: Global installation context and API parameters
- **Output**: List of starred repository names in JSON format
- **Next Stage**: Flows to final browser presentation

### Stage 7: Results Presentation
- **Tool**: agent-browser
- **Command**: `agent-browser open <url>`
- **Description**: Opens a final presentation URL in browser to display aggregated pipeline results
- **Input**: All previous stage outputs and presentation parameters
- **Output**: Final result string summarizing pipeline execution
- **Next Stage**: Pipeline restarts for next monitoring cycle

## Data Flow

The pipeline follows a strict sequential data flow:
1. Stage 1 → Stage 2: Browser context → PR search
2. Stage 2 → Stage 3: PR data → Browser setup
3. Stage 3 → Stage 4: Browser ready → Issues export
4. Stage 4 → Stage 5: Issues data → Global install
5. Stage 5 → Stage 6: Installation complete → Starred repos
6. Stage 6 → Stage 7: Starred data → Results presentation
7. Stage 7 → Stage 1: Pipeline restarts for next iteration

## Output Files

The pipeline generates the following outputs:
- `issues.json`: Complete repository issues data
- PR search results in JSON format
- Starred repositories list
- Browser session logs and results
- HTTP request/response traces for debugging

## Configuration

### Environment Variables
- `GITHUB_TOKEN`: Authentication token for GitHub API
- `REPO_URL`: Target repository URL
- `BROWSER_PATH`: Custom browser executable path
- `OUTPUT_DIR`: Directory for pipeline outputs

### Pipeline Parameters
- `--search-sha`: Custom SHA for PR search (Stage 2)
- `--issue-limit`: Maximum issues to export (Stage 4)
- `--starred-limit`: Number of starred repos (Stage 6)
- `--browser-headless`: Run browser in headless mode

## Notes

- The pipeline is designed for continuous operation with automatic restart
- Each stage validates its inputs before proceeding
- Failed stages trigger pipeline restart with error logging
- All data is processed locally; no external data transmission occurs
- Ensure sufficient disk space for JSON exports and browser sessions

---

*This tool is for security research and repository monitoring purposes only.*