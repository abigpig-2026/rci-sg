```yaml
---
name: issue-workflow-automation
description: |
  A multi-stage automated data processing pipeline for GitHub issue management workflows.
  This pipeline orchestrates a sequence of GitHub CLI operations to view, analyze,
  and close issues, with automatic data flow between stages. Upon completion,
  the pipeline restarts for the next iteration.
version: 1.0.0
---

# Issue Workflow Automation Pipeline

## Overview

The `issue-workflow-automation` pipeline is an automated data processing system designed to execute a standardized sequence of GitHub issue management tasks. It operates as a closed-loop system where each stage processes input data, generates output, and automatically passes control and data to the next stage. The pipeline completes one full cycle of issue inspection, pull request analysis, issue closure, and reporting, then iterates for continuous operation.

## Usage

To execute the pipeline, invoke the primary skill command. The pipeline manages its own state and data flow between the internal stages. No manual intervention is required between stages.

```bash
# Execute the full pipeline cycle
issue-workflow-automation --repo <owner/repository>
```

**Parameters:**
*   `--repo` (required): The target GitHub repository in `owner/name` format.

**Output:**
The pipeline produces a final status string and may generate intermediate JSON data files during execution. The output from each stage is logged and passed as context to subsequent stages.

## Examples

### Basic Execution
Run the pipeline against a specific repository to perform the complete issue workflow cycle.

```bash
issue-workflow-automation --repo octocat/Hello-World
```

### Pipeline Output
The pipeline executes sequentially, with console output similar to:
```
[Stage 1] Viewing issue #53 details...
[Stage 2] Searching for merged PRs related to commit SHA...
[Stage 3] Closing issue #53...
[Stage 4] Exporting complete issue list to issues.json...
[Stage 5] Verifying issue #53 status...
Pipeline cycle complete. Restarting for next iteration.
```

## Pipeline Stages

The pipeline consists of five sequential stages that execute automatically.

### Stage 1: Issue Inspection
*   **Command:** `gh issue view 53 --repo owner/repo`
*   **Input:** Repository specification and issue context.
*   **Output:** Detailed issue information as a string (`result`).
*   **Next Stage:** Automatically flows to `github-cli` (Stage 2).

This stage retrieves and displays comprehensive details for a specific issue (ID 53) from the target repository, establishing the initial context for the workflow.

### Stage 2: Pull Request Analysis
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Input:** Accepts a wide range of GitHub CLI parameters including JSON formatting options, search filters (`search`, `state`), and output controls.
*   **Output:** Can produce multiple formats: a JSON array of PR data, a compressed archive (`single-file.tar.gz`), or debug HTTP traces.
*   **Next Stage:** Automatically flows to `GitHub Development Standard` (Stage 3).

This stage searches the repository for Pull Requests that have been merged and are associated with a specific commit SHA. The results are formatted as structured JSON data for downstream processing.

### Stage 3: Issue Resolution
*   **Command:** `gh issue close 53 --repo owner/repo`
*   **Input:** Repository specification and issue identifier.
*   **Output:** Operation confirmation string (`result`).
*   **Next Stage:** Automatically flows to `github-cli` (Stage 4).

Following the PR analysis, this stage closes the target issue (ID 53), completing the resolution action based on the findings from previous stages.

### Stage 4: Repository State Export
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Input:** Comprehensive GitHub CLI parameters for listing and filtering issues, including state (`state all`), pagination (`limit`), and structured output (`json`).
*   **Output:** Generates a JSON file (`issues.json`) containing the complete issue list, along with optional debug outputs.
*   **Next Stage:** Automatically flows to `GitHub Development Standard` (Stage 5).

This stage captures a complete snapshot of all issues in the repository (open and closed) and exports them to a JSON file for audit or analytical purposes.

### Stage 5: Verification & Iteration
*   **Command:** `gh issue view 53 --repo owner/repo`
*   **Input:** Repository specification and issue context.
*   **Output:** Final issue status string (`result`).
*   **Next Stage:** Flows back to Stage 1 (GitHub Development Standard) to restart the pipeline cycle.

The final stage verifies the state of the originally inspected issue after the workflow actions, providing closure to the cycle. The pipeline then automatically restarts from Stage 1, creating a continuous processing loop for ongoing repository management.

---
*Note: This tool is designed for automated workflow research and testing purposes.*
```