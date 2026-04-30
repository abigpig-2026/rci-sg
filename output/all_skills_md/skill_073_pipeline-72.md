```yaml
---
name: repo-analysis-pipeline
description: A multi-stage automated data processing pipeline for GitHub repository analysis and research.
version: 1.0.0
---

# Repo Analysis Pipeline

The Repo Analysis Pipeline is an automated, multi-stage data processing system designed to perform iterative research and analysis on GitHub repositories. It orchestrates a sequence of GitHub CLI operations and custom research scripts, with data automatically flowing between stages. Upon completion of a full cycle, the pipeline can be configured to restart for continuous monitoring or iterative refinement of search criteria.

## Usage

To execute the pipeline, ensure you have the following prerequisites installed and configured:
-   **GitHub CLI (`gh`)**: Authenticated and ready for use.
-   **Node.js**: Required to run the `github-search.js` research script.
-   **`github-search.js`**: A companion JavaScript CLI tool for advanced repository searches. It should accept parameters like `language`, `limit`, `min-stars`, `updated-within`, and `output` format (`table`, `csv`, `json`).

The pipeline runs sequentially. The output of one stage typically serves as input or context for the next.

**Basic Execution:**
```bash
# The pipeline stages would be executed in order, often scripted or orchestrated by a tool.
# Example conceptual script flow:
./execute_pipeline.sh
```

**Key Configuration Points:**
*   **Authentication:** The initial `gh auth login` stage sets the security context.
*   **Research Parameters:** Criteria like `language`, `min-stars`, and `topic` are passed to the research stages.
*   **Output Handling:** Results are saved as JSON files (e.g., `/tmp/gh_results.json`, `results/${safe_topic}.json`) for persistence between stages.

## Examples

### Example 1: Full Pipeline Execution
This example outlines a single iteration of the pipeline, analyzing repositories related to "machine-learning".

1.  **Stage 1 (Auth & Setup):** `gh auth login` establishes the session.
2.  **Stage 2 (Initial Research):** `node github-search.js table --topic machine-learning --limit 50 --min-stars 1000` produces an initial table view and saves raw JSON data.
3.  **Stage 3 (PR Analysis):** `gh pr list --search "SHA_HERE" --state merged --json number,title,url` queries pull request data for commits identified in the previous research.
4.  **Stage 4 (Detailed Export):** `node github-search.js csv --language Python --updated-within 30days` exports a detailed CSV from the refined dataset.
5.  **Stage 5 (CI Watch):** `gh run watch` monitors ongoing workflows, sending a system notification upon completion.
6.  **Stage 6 (Final Data Export):** `node github-search.js json --output results/final_analysis.json` creates a final, structured JSON report.
7.  **Stage 7 (Session Refresh):** `gh auth login` re-authenticates, preparing the system for the next pipeline iteration.

### Example 2: Targeting a Specific Language
A focused run to analyze recent, popular Go projects.

```bash
# Conceptual parameter set for the research stages
RESEARCH_PARAMS="--language Go --min-stars 500 --updated-within 7days --limit 30"
# The pipeline would inject these parameters into stages 2, 4, and 6.
```

## Pipeline Stages

The pipeline consists of seven distinct stages that execute in a strict sequence. Data flows unidirectionally, with the output of one stage often informing the operation of the next.

| Stage | Name | Description | Primary Input | Output | Next Stage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Authentication & Initialization** | Establishes an authenticated session with the GitHub API using `gh auth login`. This is the foundational security step for all subsequent operations. | CLI flags and tokens for authentication. | Authentication context and session state. | `github-research` |
| 2 | **Broad Repository Research (Table)** | Executes a broad search using a custom JS CLI (`github-search.js`) configured for a human-readable `table` output. Identifies an initial set of target repositories based on configurable criteria. | Search parameters: `topic`, `language`, `limit`, `min-stars`, etc. | A terminal table view and a persistent JSON file (`/tmp/gh_results.json`). | `github-cli` |
| 3 | **Pull Request Analysis** | Uses the GitHub CLI (`gh pr list`) to perform deep analysis on the repositories identified in Stage 2. Searches for merged pull requests related to specific commits. | Repository data and commit SHAs from Stage 2 output. | Structured JSON data about relevant pull requests (numbers, titles, URLs). | `github-research` |
| 4 | **Focused Data Export (CSV)** | Runs a second, more focused research query with `github-search.js`, this time outputting in `csv` format. This stage refines the dataset based on insights from the PR analysis. | Refined criteria from Stage 3 results (e.g., specific authors, timeframes). | A CSV-formatted data file and an updated JSON results file. | `github-cli` |
| 5 | **Continuous Integration Monitor** | Monitors GitHub Actions workflow runs (`gh run watch`) for repositories in the dataset. Provides real-time feedback and a system notification upon completion. | Repository contexts and workflow IDs from the accumulated data. | CI/CD status logs and a system notification ("CI done!"). | `github-research` |
| 6 | **Final Aggregated Export (JSON)** | Executes the final research query with `github-search.js` in `json` mode. Produces a comprehensive, structured data package representing the full analysis cycle. | All aggregated parameters and filters from the previous stages. | A final, versioned JSON report file (`results/${safe_topic}.json`). | `github-cli` |
| 7 | **Session Renewal** | Re-runs `gh auth login` to refresh the authentication token and ensure the pipeline is ready for an immediate subsequent iteration without manual intervention. | Session refresh flags. | A renewed, authenticated CLI session. | `github-cli` (Loop to Stage 1) |

**Pipeline Flow Summary:**  
`Auth (CLI) → Broad Search (JS) → Deep Dive (CLI) → Focused Export (JS) → CI Watch (CLI) → Final Export (JS) → Session Renewal (CLI) → [Loop]`

*Note: This tool is designed for automated data aggregation and analysis. Ensure compliance with GitHub's Terms of Service and API rate limits when configuring pipeline execution frequency.*
```