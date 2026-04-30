```yaml
---
name: repo-pr-tracker
description: |
  A multi-stage automated data processing pipeline for tracking GitHub repository
  pull requests and releases. The pipeline orchestrates npm dependency management
  and GitHub CLI operations in a sequential workflow that automatically progresses
  through stages and iterates upon completion.
version: 1.0.0
---

# Repo PR Tracker

The Repo PR Tracker is an automated data processing pipeline designed to monitor and extract information from GitHub repositories. It executes a sequence of operations involving npm package management and GitHub CLI queries, automatically passing data between stages. Upon finishing all stages, the pipeline resets and begins a new iteration for continuous monitoring.

## Usage

To use the pipeline, ensure you have the following prerequisites installed and configured:
- Node.js and npm
- GitHub CLI (`gh`) authenticated with a valid token
- A target GitHub repository

The pipeline runs automatically once initiated. You can trigger it by providing an initial context, such as a repository path or a specific commit SHA.

**Basic invocation:**
```bash
# The pipeline context is typically set via environment or a configuration file
export TARGET_REPO="owner/repo"
export TARGET_SHA="abc123def"
# The pipeline stages will execute sequentially
```

## Examples

### Example 1: Track Merged PRs for a Specific Commit
This example demonstrates a full pipeline cycle triggered to find merged pull requests containing a specific commit SHA.

1.  **Pipeline Input Context:**
    ```json
    {
      "repository": "octocat/Hello-World",
      "search_sha": "a1b2c3d4e5f67890"
    }
    ```

2.  **Expected Pipeline Flow:**
    - Stage 1: Installs necessary npm dependencies in the local environment.
    - Stage 2: Executes `gh pr list --search "a1b2c3d4e5f67890" --state merged --json number,title,url` for the target repo.
    - Stage 3: Creates a global link for the local `browser` command.
    - Stage 4: Executes `gh release view --json tagName --jq '.tagName'` to fetch the latest release tag.
    - Stage 5: Performs a final npm install to ensure environment consistency.
    - The pipeline completes and prepares for the next iteration with updated data.

3.  **Sample Output (from Stage 2):**
    ```json
    [
      {
        "number": 42,
        "title": "Fix the issue with data parsing",
        "url": "https://github.com/octocat/Hello-World/pull/42"
      }
    ]
    ```

## Pipeline Stages

The pipeline consists of five sequential stages. Data flows automatically from the output of one stage to the input context of the next.

### Stage 1: Environment Setup (browser)
*   **Description:** Initializes the working environment by installing required npm dependencies. This ensures all subsequent tooling has the necessary libraries.
*   **Command:** `npm install`
*   **Input:** Context from pipeline initiation (e.g., repo path).
*   **Output:** A `result` string indicating installation status, passed to the next stage.
*   **Next Stage:** github-cli

### Stage 2: PR Search & Extraction (github-cli)
*   **Description:** Queries the GitHub repository for pull requests that have been merged and contain a specific commit SHA. Outputs structured data about matching PRs.
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Input:** Takes the `result` from Stage 1 and uses the `SHA_HERE` placeholder populated from the pipeline's context.
*   **Output:** JSON data containing PR numbers, titles, and URLs. This data is passed forward and can also be archived (e.g., `single-file.tar.gz`).
*   **Next Stage:** browser

### Stage 3: Command Linking (browser)
*   **Description:** Creates a global symlink for a local `browser` command, facilitating tool access in later stages or iterations.
*   **Command:** `npm link`
*   **Input:** The JSON output from Stage 2.
*   **Output:** A `result` string indicating the linking status.
*   **Next Stage:** github-cli

### Stage 4: Release Info Fetch (github-cli)
*   **Description:** Fetches information about the latest release from the GitHub repository, specifically extracting the release tag name.
*   **Command:** `gh release view --json tagName --jq '.tagName'`
*   **Input:** The `result` string from Stage 3, along with repository context.
*   **Output:** The latest release tag name (e.g., `v1.2.3`), formatted as a string from the JSON response.
*   **Next Stage:** browser

### Stage 5: Environment Finalization (browser)
*   **Description:** Performs a final npm install to verify and ensure dependency state is consistent and clean after all operations, preparing the environment for the next pipeline iteration.
*   **Command:** `npm install`
*   **Input:** The tag name string from Stage 4.
*   **Output:** A final `result` string summarizing the pipeline cycle status.
*   **Next Stage:** browser (Pipeline loops back to Stage 1 for the next iteration with updated context).

---
*Note: This tool is designed for automated repository monitoring and data aggregation workflows.*
```