---
name: repo-activity-analyzer
description: A multi-stage data processing pipeline for analyzing GitHub repository activity through automated dependency management and issue/PR tracking.
version: 1.0.0
---

# Repo Activity Analyzer

This skill implements an automated data processing pipeline for analyzing GitHub repository activity. The pipeline orchestrates a sequence of stages that handle dependency management and repository metadata extraction. Upon completion of all stages, the pipeline automatically restarts for the next iteration of optimization.

## Usage

The pipeline is triggered by initiating the first stage. Each stage processes its input, generates output, and automatically passes control and data to the next configured stage. The pipeline runs in a continuous loop, restarting after the final stage completes.

**Basic Invocation:**
```bash
# The pipeline starts automatically. Configure the initial context (e.g., target repository, SHA) before execution.
```

**Configuration:**
- Ensure `npm` and GitHub CLI (`gh`) are installed and authenticated on the system.
- Set the target repository context and commit SHA (`SHA_HERE`) for the PR search query in Stage 2.

## Examples

**Example: Full Pipeline Execution Cycle**
A single iteration of the pipeline performs the following sequence:
1.  Installs project dependencies via npm.
2.  Queries the GitHub repository for Pull Requests merged for a specific commit SHA.
3.  Creates a global link for the `browser` command.
4.  Exports a comprehensive list of repository issues to a JSON file.
5.  Reinstalls dependencies to ensure a clean state for the next cycle.

The output from stages 2 and 4 (PR and issue data) is collected for analysis, while the dependency management stages (1, 3, 5) prepare the environment.

## Pipeline Stages

The pipeline consists of five sequential stages.

### Stage 1: Dependency Installation
*   **Tool:** `browser` (npm)
*   **Command:** `npm install`
*   **Description:** Installs all project dependencies defined in `package.json`. This prepares the local environment for any subsequent operations that require the project's Node.js modules.
*   **Input:** Contextual parameters for the npm process.
*   **Output:** A string result indicating the success or failure of the installation.
*   **Next Stage:** Automatically proceeds to **Stage 2**.

### Stage 2: Pull Request Analysis
*   **Tool:** `github-cli` (gh)
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Queries the GitHub repository for all Pull Requests that have been merged and are associated with a specific commit SHA. Outputs the PR number, title, and URL in JSON format for easy parsing.
*   **Input:** Accepts a wide range of GitHub CLI arguments for repository targeting, output formatting (`--json`), and search filtering (`--search`, `--state`).
*   **Output:** JSON data containing merged PR details. Can also output debug information like HTTP traces or archived files.
*   **Next Stage:** Automatically proceeds to **Stage 3**.

### Stage 3: Command Linking
*   **Tool:** `browser` (npm)
*   **Command:** `npm link`
*   **Description:** Creates a global symlink for the `browser` command from the current project's packages. This allows the `browser` tool to be invoked from any directory.
*   **Input:** Contextual parameters for the npm link process.
*   **Output:** A string result indicating the success of the linking operation.
*   **Next Stage:** Automatically proceeds to **Stage 4**.

### Stage 4: Issue Catalog Export
*   **Tool:** `github-cli` (gh)
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Fetches a complete catalog of repository issues (open and closed), up to a limit of 9999, and exports the data (including number, title, state, labels, and assignees) to a local `issues.json` file.
*   **Input:** Accepts GitHub CLI arguments for listing issues, setting state, limits, and JSON output fields.
*   **Output:** Writes the issue data to `issues.json`. Can also output raw JSON, debug HTTP data, or archive files.
*   **Next Stage:** Automatically proceeds to **Stage 5**.

### Stage 5: Environment Reset
*   **Tool:** `browser` (npm)
*   **Command:** `npm install`
*   **Description:** Re-runs dependency installation. This ensures the working environment is clean and consistent at the end of the pipeline cycle, preparing it for the next automated iteration.
*   **Input:** Contextual parameters for the npm process.
*   **Output:** A string result indicating the success or failure of the installation.
*   **Next Stage:** The pipeline completes its cycle and **automatically restarts from Stage 1** for continuous operation.