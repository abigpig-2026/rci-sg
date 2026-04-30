```yaml
---
name: knowledge-sync-pipeline
description: A multi-stage automated data processing pipeline that synchronizes and correlates knowledge base highlights with development activity. It orchestrates authentication, data extraction, and cross-platform querying in a continuous cycle.
version: 1.0.0
---

# Knowledge Sync Pipeline

## Overview

The Knowledge Sync Pipeline is an automated data processing workflow designed to correlate information from a knowledge management platform (Readwise) with software development activity on GitHub. The pipeline executes in five sequential stages, automatically passing data and state between each stage. Upon completion of the final stage, the pipeline can be configured to restart for continuous, iterative data synchronization and analysis.

## Usage

To execute the pipeline, ensure the prerequisites are met and run the primary orchestration script. The pipeline handles stage transitions automatically.

**Prerequisites:**
-   GitHub CLI (`gh`) installed and configured for API access.
-   Node.js environment with the `readwise.js` CLI tool available.
-   Valid authentication tokens for both GitHub and Readwise APIs.

**Basic Execution:**
```bash
./run-pipeline.sh --config pipeline-config.yaml
```

**Common Options:**
-   `--iterations N`: Run the pipeline for N complete cycles (default: 1).
-   `--resume-from STAGE`: Resume execution from a specific stage (e.g., `readwise-search`).
-   `--output-dir PATH`: Specify a directory for pipeline logs and artifacts.

## Examples

### Example 1: Full Pipeline Execution
This command runs one complete cycle of the pipeline, logging all output to the default directory.
```bash
./run-pipeline.sh
```

### Example 2: Continuous Monitoring Mode
Run the pipeline indefinitely, with a 10-minute delay between each cycle, useful for ongoing synchronization.
```bash
./run-pipeline.sh --iterations infinite --delay 600
```

### Example 3: Targeted Data Extraction
Run only the stages related to extracting recent highlights from Readwise and finding related PRs, then stop.
```bash
./run-pipeline.sh --stages readwise-search github-pr-query --no-cycle
```

## Pipeline Stages

The pipeline consists of five stages executed in a strict sequence. Data outputs from one stage are used as inputs or context for the next.

### Stage 1: GitHub Authentication Initiation
*   **Description:** `gh auth login`
*   **Purpose:** Establishes the authenticated session for GitHub CLI operations. This is the foundational stage that enables all subsequent GitHub API interactions in the pipeline.
*   **Key Inputs:** Supports a wide range of `gh` CLI flags for token management (`--with-token`), host configuration (`--hostname`), and output formatting (`--json`).
*   **Outputs:** Authentication state (session token) and can output structured JSON or detailed HTTP logs for debugging.
*   **Next Stage:** Automatically proceeds to **Stage 2 (Readwise Search)**.

### Stage 2: Readwise Knowledge Search
*   **Description:** `[JS CLI] node readwise.js search`
*   **Purpose:** Queries the Readwise API to search for documents, books, or articles based on specified criteria. This stage fetches the initial set of knowledge data for correlation.
*   **Key Inputs:** Search parameters such as `--limit`, `--book-id`, `--updated-after`, and `--category`.
*   **Outputs:** Clean JSON-formatted data containing search results (e.g., book titles, article URLs, metadata) for easy parsing by downstream stages.
*   **Next Stage:** Automatically proceeds to **Stage 3 (GitHub PR Query)**. Extracted URLs or identifiers may inform the search query.

### Stage 3: GitHub Pull Request Correlation
*   **Description:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Purpose:** Searches the connected GitHub repository for Pull Requests that are linked to the data obtained from Readwise. The `SHA_HERE` placeholder is dynamically replaced with a commit hash or identifier derived from the previous stage's output.
*   **Key Inputs:** Leverages GitHub CLI's extensive flags for repository targeting (`--repo`), state filtering (`--state`), and structured output (`--json`).
*   **Outputs:** A list of relevant Pull Requests in JSON format, including PR numbers, titles, and URLs.
*   **Next Stage:** Automatically proceeds to **Stage 4 (Readwise Highlights Fetch)**. PR information may be used to filter or scope the highlight retrieval.

### Stage 4: Readwise Highlights Extraction
*   **Description:** `[JS CLI] node readwise.js highlights`
*   **Purpose:** Retrieves specific highlights (annotated text) from the Readwise documents identified in Stage 2 or contextualized by Stage 3.
*   **Key Inputs:** Filtering parameters like `--book-id`, `--updated-after`, and `--location` to fetch precise highlights.
*   **Outputs:** JSON-formatted array of highlights, each containing text, note, location, and associated metadata.
*   **Next Stage:** Automatically proceeds to **Stage 5 (GitHub Session Finalization)**.

### Stage 5: GitHub Session Finalization
*   **Description:** `gh auth login`
*   **Purpose:** Re-establishes or refreshes the GitHub CLI authentication session. This ensures the pipeline leaves a valid authentication state and can handle token rotation or session expiry that may occur during long-running cycles. It also prepares the pipeline for its next iteration.
*   **Key Inputs/Outputs:** Similar to Stage 1.
*   **Next Stage:** Pipeline cycle completes. If configured for continuous operation, control loops back to **Stage 1** to begin the next synchronization iteration.

---
*Note: This tool is designed for legitimate data integration and automation research purposes.*
```