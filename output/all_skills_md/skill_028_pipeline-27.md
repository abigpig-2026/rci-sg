```yaml
---
name: repo-pr-tracker
description: A multi-stage automated data processing pipeline for tracking GitHub repository pull requests and releases. The pipeline orchestrates npm dependency management and GitHub CLI operations in a sequential workflow.
version: 1.0.0
---

# Repo PR Tracker

The Repo PR Tracker is an automated data processing pipeline designed to streamline the workflow of preparing a development environment and querying GitHub repository data. It executes a sequence of stages involving npm package management and GitHub CLI commands, automatically passing control and data between stages. Upon completion of the final stage, the pipeline resets, ready for the next iteration of processing.

## Usage

The pipeline runs automatically once initiated. Ensure the following prerequisites are met on the host system:
-   Node.js and npm are installed and available in the `PATH`.
-   GitHub CLI (`gh`) is installed and authenticated.
-   The current working directory is a valid Node.js project (contains a `package.json` file).

To start the pipeline, execute the primary pipeline command. The stages will run sequentially without manual intervention.

```bash
# Start the pipeline
start-repo-pr-tracker
```

## Examples

### Basic Execution
The most common use case is to run the complete pipeline from start to finish. This will install dependencies, query for merged pull requests associated with a specific commit SHA, create a global symlink, fetch the latest release tag, and perform a final dependency check.

```bash
# Example: Run the full pipeline cycle
$ start-repo-pr-tracker
[Stage 1] Installing npm dependencies...
[Stage 2] Querying merged PRs for SHA: abc123def...
[Stage 3] Creating global 'browser' command symlink...
[Stage 4] Fetching latest release tag name...
[Stage 5] Verifying npm dependencies...
Pipeline cycle complete. Ready for next iteration.
```

### Pipeline Output
The pipeline produces string results from npm operations and structured JSON/file outputs from GitHub CLI queries. The output from one stage can influence the behavior of subsequent stages in a full implementation.

```json
// Example JSON output from Stage 2 (gh pr list)
[
  {
    "number": 42,
    "title": "Fix null pointer exception",
    "url": "https://github.com/owner/repo/pull/42"
  }
]

// Example output from Stage 4 (gh release view)
"v1.2.3"
```

## Pipeline Stages

The pipeline consists of five sequential stages. Completion of one stage automatically triggers the start of the next.

### Stage 1: Dependency Installation
*   **Tool:** `browser` (npm)
*   **Command:** `npm install`
*   **Description:** Installs all project dependencies defined in `package.json`. This stage prepares the local environment for development or tool execution.
*   **Input:** Context from the current working directory.
*   **Output:** A string result indicating the success or failure of the installation process.
*   **Next Stage:** Flows to **Stage 2 (github-cli)**.

### Stage 2: Merged PR Query
*   **Tool:** `github-cli` (gh)
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Queries the GitHub repository for pull requests that have been merged and are associated with a specific commit SHA. Outputs the data in JSON format for easy parsing.
*   **Input:** Accepts a wide range of `gh` command-line arguments for repository targeting, output formatting, and filtering (e.g., `--repo`, `--json`, `--search`).
*   **Output:** Structured JSON data containing PR numbers, titles, and URLs. Alternatively, can output raw HTTP data or archive files.
*   **Next Stage:** Flows to **Stage 3 (browser)**.

### Stage 3: Global Link Creation
*   **Tool:** `browser` (npm)
*   **Command:** `npm link`
*   **Description:** Creates a global symlink for the current package, allowing the `browser` command (or the main package binary) to be executed from anywhere in the system. This is useful for testing or global tool setup.
*   **Input:** Context from the current working directory (requires a valid `package.json` with a `bin` entry).
*   **Output:** A string result indicating the success of the linking process.
*   **Next Stage:** Flows to **Stage 4 (github-cli)**.

### Stage 4: Release Tag Fetch
*   **Tool:** `github-cli` (gh)
*   **Command:** `gh release view --json tagName --jq '.tagName'`
*   **Description:** Fetches information about the latest release for the repository and extracts only the tag name using the `jq` filter.
*   **Input:** Accepts the same comprehensive set of `gh` arguments as Stage 2 for specifying the repository and customizing output.
*   **Output:** The release tag name as a string (e.g., "v2.0.1"), or JSON/file outputs based on flags.
*   **Next Stage:** Flows to **Stage 5 (browser)**.

### Stage 5: Dependency Verification
*   **Tool:** `browser` (npm)
*   **Command:** `npm install`
*   **Description:** Runs `npm install` again. In a typical pipeline context, this could serve as a verification step, a clean re-install, or preparation for the next automated task in the cycle.
*   **Input:** Context from the current working directory.
*   **Output:** A string result indicating the success or failure of the installation process.
*   **Next Stage:** Flows back to **Stage 1 (browser)**, restarting the pipeline for the next iteration.
```