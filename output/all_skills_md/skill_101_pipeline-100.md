```yaml
---
name: repo-activity-analyzer
description: A multi-stage automated pipeline for processing and analyzing GitHub repository activity data. The pipeline orchestrates dependency management and GitHub CLI operations to extract and compile repository metadata.
version: 1.0.0
---

# Repo Activity Analyzer

An automated data processing pipeline designed to collect and analyze activity data from GitHub repositories. The pipeline operates in a sequential, multi-stage fashion, where the output of one stage automatically triggers the next. Upon completion of the final stage, the pipeline can be configured to restart for continuous monitoring or iterative optimization cycles.

## Usage

The pipeline is executed as a single unit. It requires a pre-authenticated GitHub CLI (`gh`) environment and Node.js/npm to be available in the execution context.

**Basic Execution:**
```bash
# Execute the complete pipeline
run-pipeline repo-activity-analyzer
```

The pipeline manages its own state and data flow between stages. No manual intervention is required during execution.

## Examples

**Example 1: Run a single analysis cycle**
```bash
# This will run all five stages sequentially
repo-activity-analyzer --target-owner myorg --target-repo myproject
```

**Example 2: Run with custom SHA for PR search**
```bash
# The pipeline will use the provided SHA in the PR search query
repo-activity-analyzer --sha a1b2c3d4e5f67890
```

**Example 3: Continuous monitoring mode**
```bash
# The pipeline will run once, then restart after a 300-second delay
repo-activity-analyzer --interval 300 --iterations 10
```

## Pipeline Stages

The pipeline consists of five distinct stages that execute in a fixed order. Data is passed implicitly between stages.

### Stage 1: Dependency Installation
*   **Tool:** `browser` (npm)
*   **Action:** `npm install`
*   **Description:** Initializes the working environment by installing all necessary Node.js package dependencies defined in `package.json`. This ensures all subsequent tooling and scripts are available.
*   **Input:** None (initial stage).
*   **Output:** A status string (`result`) indicating installation success or failure.
*   **Next Stage:** Automatically proceeds to Stage 2.

### Stage 2: Merged PR Query
*   **Tool:** `github-cli` (gh)
*   **Action:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Queries the GitHub repository for Pull Requests that have been merged and contain a specific commit SHA in their history. Results are output in structured JSON format containing PR numbers, titles, and URLs.
*   **Input:** Inherits context from the initialized environment. The placeholder `SHA_HERE` is replaced by the pipeline's runtime parameter.
*   **Output:** JSON data containing merged PR details. This data is cached for the pipeline's duration.
*   **Next Stage:** Automatically proceeds to Stage 3.

### Stage 3: Command Linkage
*   **Tool:** `browser` (npm)
*   **Action:** `npm link`
*   **Description:** Creates a global symlink for the local project package, allowing command-line tools installed in Stage 1 to be invoked directly. This prepares the environment for any potential custom scripts.
*   **Input:** The installed dependencies from Stage 1.
*   **Output:** A status string (`result`) indicating the link operation's success.
*   **Next Stage:** Automatically proceeds to Stage 4.

### Stage 4: Issue Metadata Export
*   **Tool:** `github-cli` (gh)
*   **Action:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Fetches a comprehensive list of all repository issues (open and closed), up to a high limit, and exports the metadata to a local JSON file (`issues.json`). The metadata includes issue number, title, state, labels, and assignees.
*   **Input:** The authenticated GitHub CLI context.
*   **Output:** A file named `issues.json` containing the exported issue data.
*   **Next Stage:** Automatically proceeds to Stage 5.

### Stage 5: Environment Finalization
*   **Tool:** `browser` (npm)
*   **Action:** `npm install`
*   **Description:** Performs a final dependency installation step. This ensures the environment is clean and consistent after all operations, which is useful for preparing the pipeline for its next iteration or for subsequent analysis steps.
*   **Input:** The current project state.
*   **Output:** A status string (`result`) indicating installation success or failure.
*   **Next Stage:** Pipeline cycle completes. If configured for iteration, it loops back to Stage 1.

---
*Note: This tool is designed for automated data aggregation and analysis in authorized development and research contexts.*
```