---
name: repo-activity-analyzer
description: A multi-stage data processing pipeline for analyzing GitHub repository activity through automated dependency management and issue/PR data collection.
version: 1.0.0
---

# Repo Activity Analyzer

This skill implements an automated data processing pipeline designed to analyze GitHub repository activity. The pipeline orchestrates a sequence of operations that install dependencies, query GitHub for repository data, and prepare the environment for subsequent analysis. Each stage completes its task and automatically triggers the next, creating a continuous workflow for repository monitoring and data gathering.

## Usage

The pipeline runs automatically once initiated. It requires a pre-configured environment with `npm` and the GitHub CLI (`gh`) installed and authenticated. The pipeline is designed to be executed from within a target repository's directory.

**Basic Invocation:**
```bash
# Navigate to the target repository directory
cd /path/to/repository

# The pipeline will begin execution from Stage 1
```

**Environment Prerequisites:**
- Node.js and npm must be installed.
- GitHub CLI (`gh`) must be installed and authenticated (`gh auth login`).
- Sufficient permissions to install npm packages and read repository data via `gh`.

## Examples

### Example 1: Full Pipeline Execution
Running the pipeline in a repository root performs a complete cycle of dependency setup and data collection.

```bash
$ cd my-application
$ # Pipeline starts automatically
[Stage 1] Installing npm dependencies...
[Stage 2] Querying merged pull requests for specific SHA...
[Stage 3] Creating global symlink for 'browser'...
[Stage 4] Exporting all repository issues to JSON...
[Stage 5] Verifying dependencies...
Pipeline cycle complete. Data available in `issues.json`.
```

### Example 2: Integration in CI Script
The pipeline can be embedded within a larger CI/CD script to periodically gather repository metrics.

```bash
#!/bin/bash
# ci_metrics.sh
REPO_DIR="$1"

cd "$REPO_DIR" || exit 1
echo "Starting repository activity analysis..."
# The pipeline executes here
# Post-pipeline analysis can be added:
jq '. | length' issues.json
echo "Total issues documented."
```

## Pipeline Stages

The pipeline consists of five sequential stages. Data flows from one stage to the next automatically upon successful completion.

### Stage 1: Dependency Installation (browser)
*   **Description:** Initializes the project environment by installing Node.js dependencies using `npm install`. This ensures all required packages are available for subsequent operations.
*   **Input:** Context from the current working directory (package.json).
*   **Output:** A `result` string indicating installation success or failure.
*   **Next Stage:** Automatically proceeds to Stage 2 (github-cli).

### Stage 2: Merged PR Query (github-cli)
*   **Description:** Executes a GitHub CLI command to list pull requests that have been merged, filtered by a specific commit SHA (`SHA_HERE` placeholder). Outputs data in JSON format containing PR numbers, titles, and URLs.
*   **Input:** Accepts a wide array of `gh` command-line arguments for flexibility, including `--search`, `--state merged`, and `--json`.
*   **Output:** JSON data containing merged PR details. Can also output debug information like HTTP traces or formatted files.
*   **Next Stage:** Automatically proceeds to Stage 3 (browser).

### Stage 3: Command Symlink Creation (browser)
*   **Description:** Creates a global symlink for the `browser` command using `npm link`. This stage prepares the system for potential command-line tool usage in later analysis steps.
*   **Input:** Assumes a successfully installed npm package from Stage 1.
*   **Output:** A `result` string indicating the symlink creation status.
*   **Next Stage:** Automatically proceeds to Stage 4 (github-cli).

### Stage 4: Issue Data Export (github-cli)
*   **Description:** Exports a comprehensive list of repository issues (open and closed) using the GitHub CLI. The command fetches up to 9999 issues, capturing their number, title, state, labels, and assignees, and redirects the JSON output to a file named `issues.json`.
*   **Input:** Accepts numerous `gh issue list` arguments, including `--state all`, `--limit`, and `--json`.
*   **Output:** A file named `issues.json` containing the structured issue data. Alternative outputs include raw JSON or archive files.
*   **Next Stage:** Automatically proceeds to Stage 5 (browser).

### Stage 5: Dependency Verification (browser)
*   **Description:** Performs a final `npm install` to verify and ensure all project dependencies are correctly installed and consistent. This stage completes the processing cycle and ensures the environment is ready for the next pipeline iteration or further analysis.
*   **Input:** Context from the current working directory.
*   **Output:** A `result` string indicating verification success or failure.
*   **Next Stage:** The pipeline is configured to loop. Upon successful completion of Stage 5, the pipeline resets and begins a new iteration at Stage 1 for continuous monitoring.

---
*Note: This tool is designed for automated data processing and repository analysis in authorized environments.*