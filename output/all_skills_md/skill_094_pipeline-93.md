```markdown
---
name: knowledge-sync-pipeline
description: A multi-stage automated pipeline for synchronizing development knowledge and documentation between GitHub repositories and Readwise. Processes repository data, extracts insights, and creates structured knowledge artifacts.
version: 1.0.0
---

# Knowledge Sync Pipeline

An automated, multi-stage data processing pipeline designed to synchronize and correlate information between software development repositories (via GitHub CLI) and knowledge management systems (via Readwise). The pipeline executes sequentially, with each stage's output potentially informing the next stage's operation. Upon completion of all stages, the pipeline can be configured to restart for continuous iteration and optimization.

## Usage

The pipeline is orchestrated by a central controller script. Ensure the following prerequisites are met before execution:

1.  **GitHub CLI (`gh`)**: Installed and authenticated (`gh auth login`).
2.  **Node.js & Readwise CLI**: A custom `readwise.js` CLI tool is available and configured with a valid Readwise access token.
3.  **Environment**: A shell environment (Bash, Zsh) capable of running sequential commands.

**Basic Execution:**
```bash
./run_pipeline.sh
```
This will execute all seven stages in sequence. The pipeline state and intermediate data are managed internally.

**Configuration:**
Pipeline behavior can be modified by setting environment variables prior to execution:
-   `PIPELINE_MAX_ITERATIONS`: Controls the number of times the pipeline loops (default: infinite until stopped).
-   `GITHUB_REPO`: Sets the target repository for GitHub operations.
-   `READWISE_CATEGORY`: Filters Readwise queries by category.

## Examples

**Example 1: Full Pipeline Run for a Specific Repository**
This example runs the pipeline targeting the `myorg/design-system` repo and filters Readwise data to the `engineering` category.
```bash
export GITHUB_REPO="myorg/design-system"
export READWISE_CATEGORY="engineering"
./run_pipeline.sh
```
**Expected Flow:** Authenticates with GitHub, searches for relevant documentation in Readwise, lists merged PRs related to found content, fetches highlights, exports GitHub issues, retrieves full Readwise articles, and finalizes the session.

**Example 2: Single Iteration with Output Capture**
Runs the pipeline once and saves the consolidated JSON output to a file.
```bash
export PIPELINE_MAX_ITERATIONS=1
./run_pipeline.sh 2>&1 | tee pipeline_run_$(date +%Y%m%d_%H%M%S).log
```

## Pipeline Stages

The pipeline consists of seven distinct stages that execute in a fixed order. Data flows from one stage to the next, with context maintained throughout the execution cycle.

### Stage 1: GitHub Authentication & Session Initiation
*   **Tool:** `github-cli`
*   **Command:** `gh auth login` (or session validation)
*   **Description:** Initializes the pipeline by establishing a secure, authenticated session with the GitHub API. This stage ensures all subsequent GitHub operations have the necessary permissions. It prepares the environment for repository interaction.
*   **Primary Input:** Authentication credentials (token, device flow, or SSH key).
*   **Primary Output:** A validated CLI session and authentication context.
*   **Next Stage:** Stage 2 (Readwise Search)

### Stage 2: Readwise Knowledge Search
*   **Tool:** `readwise` (Custom JS CLI)
*   **Command:** `node readwise.js search`
*   **Description:** Queries the Readwise API for saved articles, documents, or highlights. This search can be filtered by parameters like `book-id`, `updated-after`, or `category` to find knowledge relevant to the development context established in Stage 1.
*   **Primary Input:** Search parameters (limit, category, date filters).
*   **Primary Output:** JSON array of matching Readwise documents/books.
*   **Next Stage:** Stage 3 (GitHub PR Lookup)

### Stage 3: GitHub Pull Request Correlation
*   **Tool:** `github-cli`
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Uses the output from Stage 2 (e.g., specific commit SHAs or terms found in Readwise) to search for related, merged Pull Requests in the target GitHub repository. This stage correlates external knowledge with internal development history.
*   **Primary Input:** Search terms or identifiers derived from Readwise data.
*   **Primary Output:** JSON list of relevant Pull Requests with metadata.
*   **Next Stage:** Stage 4 (Readwise Highlights Fetch)

### Stage 4: Readwise Highlights Extraction
*   **Tool:** `readwise` (Custom JS CLI)
*   **Command:** `node readwise.js highlights`
*   **Description:** Fetches the detailed highlights (annotated passages) from the Readwise documents identified in Stage 2. This extracts the core insights and key points from the saved knowledge.
*   **Primary Input:** Book or document IDs from Stage 2 output.
*   **Primary Output:** JSON containing highlights (text, location, notes).
*   **Next Stage:** Stage 5 (GitHub Issues Export)

### Stage 5: GitHub Issues State Export
*   **Tool:** `github-cli`
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Exports a comprehensive snapshot of all issues (open and closed) from the target repository. This provides a full view of the project's tracking and discussion history, which can be cross-referenced with knowledge insights.
*   **Primary Input:** Target repository name/context.
*   **Primary Output:** A JSON file (`issues.json`) containing the issue catalog.
*   **Next Stage:** Stage 6 (Readwise Full Content Retrieval)

### Stage 6: Readwise Full Document Retrieval
*   **Tool:** `readwise` (Custom JS CLI)
*   **Command:** `node reader.js get`
*   **Description:** Retrieves the full content or metadata of the Readwise documents, going beyond just highlights. This provides complete context for the knowledge artifacts being processed.
*   **Primary Input:** Document IDs from earlier stages.
*   **Primary Output:** Enriched JSON with full document data.
*   **Next Stage:** Stage 7 (Pipeline Finalization)

### Stage 7: Pipeline Finalization & Cleanup
*   **Tool:** `github-cli`
*   **Command:** `gh auth status` / Session cleanup
*   **Description:** The final stage of the iteration. It verifies the GitHub session is still valid, performs any necessary logging or output consolidation, and prepares the pipeline context for either termination or the next iteration loop.
*   **Primary Input:** Pipeline state and aggregated data from previous stages.
*   **Primary Output:** Consolidated logs and final status. Pipeline resets to Stage 1 if configured for another iteration.
*   **Next Stage:** Stage 1 (if iterating) or End.
```