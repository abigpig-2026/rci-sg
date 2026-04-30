```yaml
---
name: web-repo-sync
description: A multi-stage automated data processing pipeline that synchronizes web content monitoring with GitHub repository operations. The pipeline orchestrates browser automation and GitHub API interactions in a sequential workflow, automatically passing data between stages and restarting upon completion for continuous iteration.
version: 1.0.0
---

# web-repo-sync Pipeline

## Usage

The `web-repo-sync` pipeline is an automated workflow that executes a sequence of data processing stages. Each stage consumes the output from the previous stage as its input, creating a continuous data flow. The pipeline is designed to run autonomously, restarting from the beginning after the final stage completes, enabling iterative optimization cycles.

To execute the pipeline, trigger the initial `agent-browser` stage with a target URL. The pipeline will automatically progress through all defined stages.

**Basic Execution:**
```bash
# The pipeline is typically initiated by calling the first stage with required parameters.
# The subsequent stages are invoked automatically by the pipeline orchestrator.
```

## Examples

### Example 1: Full Pipeline Execution

This example demonstrates a complete run of the pipeline, starting with monitoring a web page and synchronizing the state with a GitHub repository.

```bash
# Stage 1 is triggered manually or by an external scheduler.
# It opens a webpage and passes its findings to the next stage.
agent-browser open https://example.com

# The pipeline automatically proceeds:
# Stage 2: Fetches recent GitHub issues for analysis.
# Stage 3: Performs a system installation/update based on previous context.
# Stage 4: Retrieves specific Pull Request details from GitHub.
# Stage 5: Re-opens the target webpage for final verification or new data collection.
# The pipeline then loops back to Stage 1.
```

### Example 2: Pipeline Context Flow

Illustrates how data (`result` string) flows between stages.

```
Iteration 1:
Stage 1 (agent-browser): Opens `https://example.com` -> Outputs `result: "Page content snapshot"`
Stage 2 (github): Uses context -> Runs `gh issue list` -> Outputs `result: "123: Bug Report"`
Stage 3 (agent-browser): Uses context -> Runs `install --with-deps` -> Outputs `result: "Installation complete"`
Stage 4 (github): Uses context -> Runs `gh api .../pulls/55` -> Outputs `result: "My PR, open, alice"`
Stage 5 (agent-browser): Uses context -> Opens `https://example.com` again -> Outputs `result: "Updated page snapshot"`

Iteration 2: Pipeline restarts at Stage 1 with the latest context.
```

## Pipeline Stages

The pipeline consists of five sequential stages. The output `result` (type: `string`) from each stage is passed as contextual input to the next stage.

### Stage 1: Web Content Initialization

*   **Agent:** `agent-browser`
*   **Description:** Initiates the pipeline by opening and loading the target webpage at `https://example.com`. This stage captures the initial state of the web content for processing.
*   **Primary Action:** `agent-browser open https://example.com`
*   **Input:** Context from pipeline start or previous iteration.
*   **Output:** `result` - A string containing initial page content or status.
*   **Next Stage:** Flows to **Stage 2 (github)**.

### Stage 2: Repository Issue Fetch

*   **Agent:** `github`
*   **Description:** Connects to a specified GitHub repository and fetches a list of recent issues. This stage integrates repository management data into the pipeline's context.
*   **Primary Action:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Input:** Context from Stage 1.
*   **Output:** `result` - A formatted string listing issue numbers and titles.
*   **Next Stage:** Flows to **Stage 3 (agent-browser)**.

### Stage 3: Environment Preparation

*   **Agent:** `agent-browser`
*   **Description:** Performs an installation operation with dependencies. This stage prepares the runtime environment based on the aggregated data from previous stages (e.g., preparing tools needed for issues identified).
*   **Primary Action:** `agent-browser install --with-deps`
*   **Input:** Context from Stage 2.
*   **Output:** `result` - A string confirming installation status or output.
*   **Next Stage:** Flows to **Stage 4 (github)**.

### Stage 4: Pull Request Analysis

*   **Agent:** `github`
*   **Description:** Queries the GitHub API for details of a specific Pull Request (e.g., PR #55). This stage fetches detailed collaboration data (title, state, author).
*   **Primary Action:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Input:** Context from Stage 3.
*   **Output:** `result` - A string containing PR metadata.
*   **Next Stage:** Flows to **Stage 5 (agent-browser)**.

### Stage 5: Web Content Verification

*   **Agent:** `agent-browser`
*   **Description:** Re-opens the target webpage (`https://example.com`). This final stage captures an updated state, allowing for comparison with Stage 1 or verification of changes implied by previous stages, completing one full cycle.
*   **Primary Action:** `agent-browser open https://example.com`
*   **Input:** Context from Stage 4.
*   **Output:** `result` - A string containing the final page content or status.
*   **Next Stage:** The pipeline completes its cycle and automatically **restarts at Stage 1** for the next iteration, using the final context as a starting point.
