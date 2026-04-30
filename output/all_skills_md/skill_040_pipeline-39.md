```yaml
---
name: repo-dependency-pipeline
description: A multi-stage automated data processing pipeline for repository dependency management and GitHub operations. The pipeline orchestrates npm dependency installation and GitHub CLI operations in a sequential workflow.
version: 1.0.0
---

# Repo Dependency Pipeline

## Overview

The Repo Dependency Pipeline is an automated, multi-stage data processing workflow designed to manage repository dependencies and interact with GitHub. It orchestrates a sequence of operations, alternating between local npm commands and GitHub CLI (`gh`) queries, to perform a complete repository setup and analysis cycle. Upon completion of all stages, the pipeline automatically restarts for the next iteration of optimization.

## Usage

To execute the pipeline, ensure you have the following prerequisites installed and configured:
- **Node.js** and **npm** (for `npm install` and `npm link` commands)
- **GitHub CLI (`gh`)** (authenticated with appropriate permissions)
- A valid Git repository context

The pipeline runs sequentially. The output of one stage is passed as context or triggers the next stage. No manual intervention is required between stages.

### Basic Execution
The pipeline is invoked as a single unit. The control system will handle the stage transitions based on the defined workflow.

## Examples

### Example 1: Full Pipeline Execution
This example demonstrates a complete run of the pipeline, simulating a new repository setup and initial GitHub data fetch.

```bash
# The pipeline starts automatically.
# Stage 1: Install project dependencies.
> npm install
added 250 packages in 15s

# Stage 2: Query merged Pull Requests related to a specific commit SHA.
> gh pr list --search "a1b2c3d4" --state merged --json number,title,url
[
  {
    "number": 42,
    "title": "Fix null pointer exception",
    "url": "https://github.com/owner/repo/pull/42"
  }
]

# Stage 3: Create a global link for the project's CLI tool.
> npm link
/usr/local/bin/browser -> /usr/local/lib/node_modules/my-cli/index.js

# Stage 4: Fetch a list of repositories starred by the authenticated user.
> gh api --paginate user/starred --jq '.[].full_name' | head -20
microsoft/vscode
facebook/react
nodejs/node
...

# Stage 5: Re-install dependencies (simulating a clean state for next iteration).
> npm install
already up to date

# Pipeline completes and is ready for the next iteration.
```

### Example 2: Pipeline Context
The pipeline maintains context between stages. For instance, the SHA from a commit discovered in Stage 1 could be used in the `--search` parameter for Stage 2 in a subsequent, more advanced iteration.

## Pipeline Stages

The pipeline consists of five sequential stages. Each stage must complete successfully before the next begins.

### Stage 1: Dependency Installation (browser)
*   **Description:** Initializes the project environment by installing all required npm dependencies as defined in `package.json`. This prepares the local workspace for development or analysis tasks.
*   **Input:** Context from the pipeline trigger (e.g., repository path).
*   **Output:** A `result` string indicating installation success/failure and a local `node_modules` directory.
*   **Next Stage:** Automatically proceeds to **Stage 2 (github-cli)**.

### Stage 2: PR Analysis (github-cli)
*   **Description:** Queries the GitHub repository for Pull Requests that have been merged and contain a specific commit SHA (`SHA_HERE`). This stage extracts structured data about relevant PRs.
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Input:** Accepts numerous `gh` command-line flags for customization (e.g., `--json`, `--search`, `--state`). The primary input is the search context, often derived from previous operations.
*   **Output:** JSON data containing PR numbers, titles, and URLs. Can also output debug information like raw HTTP traces.
*   **Next Stage:** Automatically proceeds to **Stage 3 (browser)**.

### Stage 3: Tool Linking (browser)
*   **Description:** Creates a global symbolic link for the project's package, allowing its command-line interface (if any) to be executed from anywhere in the system. This is typical for CLI tools built with Node.js.
*   **Command:** `npm link`
*   **Input:** Requires a successfully built/installed package from Stage 1.
*   **Output:** A `result` string confirming the link creation and a global command availability.
*   **Next Stage:** Automatically proceeds to **Stage 4 (github-cli)**.

### Stage 4: Repository Discovery (github-cli)
*   **Description:** Fetches a curated list of repositories that the authenticated GitHub user has starred. This data can be used for analysis, inspiration, or dependency research.
*   **Command:** `gh api --paginate user/starred --jq '.[].full_name' | head -20`
*   **Input:** Accepts numerous `gh api` and `gh` global flags (e.g., `--paginate`, `--jq`, `--cache`).
*   **Output:** A list of up to 20 repository full names (e.g., `owner/repo`). Can also output raw JSON or archived data.
*   **Next Stage:** Automatically proceeds to **Stage 5 (browser)**.

### Stage 5: Dependency Verification (browser)
*   **Description:** Performs a final dependency installation check to ensure the environment is consistent and ready for the next pipeline iteration or subsequent operations. This ensures a clean, reproducible state.
*   **Command:** `npm install`
*   **Input:** The current project state.
*   **Output:** A `result` string confirming dependencies are up-to-date.
*   **Next Stage:** The pipeline cycle completes. The system will restart from **Stage 1** for the next automated iteration, potentially with updated parameters or context.

---
*Note: This tool is designed for automated workflow research and integration testing.*
```