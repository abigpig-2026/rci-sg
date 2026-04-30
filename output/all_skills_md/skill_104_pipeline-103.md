```yaml
---
name: repo-analysis-pipeline
description: A multi-stage automated data processing pipeline for repository analysis and dependency management. The pipeline orchestrates browser automation and GitHub CLI operations to collect repository metrics and prepare development environments.
version: 1.0.0
---

# Repo Analysis Pipeline

An automated, multi-stage data processing pipeline designed for iterative repository analysis. The pipeline sequentially executes browser-based dependency management and GitHub CLI data collection tasks, with automatic stage-to-stage data flow. Upon completion of all stages, the pipeline resets for the next iteration of optimization.

## Usage

The pipeline is triggered with an initial context (typically a repository identifier or path). It then proceeds through its stages automatically, with the output of one stage serving as potential context for the next.

**Basic Invocation:**
```bash
# The pipeline manages its own stage progression.
# Initiate with a target repository context.
pipeline-run --target-repo "owner/repo-name"
```

**Configuration (Optional):**
Environment variables or a config file can be used to set parameters like GitHub tokens or output directories.
```bash
export GITHUB_TOKEN="ghp_..."
export OUTPUT_DIR="./analysis_results"
```

## Examples

**Example 1: Analyze a specific repository**
This run will install dependencies, query merged PRs for a specific commit SHA, link the package, fetch contributor stats, and finalize.
```bash
pipeline-run --target-repo "octocat/Hello-World" --sha "a1b2c3d4"
```

**Example 2: Run with custom output**
Direct the pipeline's file outputs to a specific location.
```bash
pipeline-run --target-repo "github/docs" --output /tmp/gh-analysis --format json
```

## Pipeline Stages

The pipeline consists of five sequential stages. Completion of a stage automatically triggers the start of the next.

### Stage 1: Dependency Installation (Browser)
*   **Description:** Initializes the project environment by installing Node.js dependencies via `npm install`.
*   **Input:** Contextual project path or initialization trigger.
*   **Output:** A `result` string indicating installation success/failure and summary.
*   **Next Stage:** Output flows automatically to **Stage 2**.

### Stage 2: PR Analysis (GitHub CLI)
*   **Description:** Queries the GitHub repository for Pull Requests merged containing a specific commit SHA. Uses the command: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`.
*   **Input:** Accepts a wide range of GitHub CLI parameters, with `search` and `json` being primary for this stage. Expects `SHA_HERE` to be provided from context.
*   **Output:** Structured JSON data of matching PRs, or optionally a raw HTTP trace file (`single-file.tar.gz`).
*   **Next Stage:** Output flows automatically to **Stage 3**.

### Stage 3: Command Linking (Browser)
*   **Description:** Creates a global symlink for the project's CLI tool using `npm link`, making it accessible system-wide.
*   **Input:** Assumes a successful `npm install` from Stage 1.
*   **Output:** A `result` string confirming the link creation.
*   **Next Stage:** Output flows automatically to **Stage 4**.

### Stage 4: Contributor Metrics (GitHub CLI)
*   **Description:** Fetches and formats contributor statistics for the repository. Uses the command: `gh api --paginate repos/owner/repo/contributors --jq '.[] | "\(.login): \(.contributions)"' | head -n [LIMIT]`.
*   **Input:** Accepts extensive GitHub CLI API and filtering options. Requires `owner` and `repo` context.
*   **Output:** A formatted list of contributors and their contribution counts, or raw JSON.
*   **Next Stage:** Output flows automatically to **Stage 5**.

### Stage 5: Dependency Finalization (Browser)
*   **Description:** Performs a final `npm install` to ensure all dependencies are correctly resolved and locked after preceding operations.
*   **Input:** Context from previous stages.
*   **Output:** A final `result` string summarizing the dependency state.
*   **Next Stage:** Pipeline cycle completes and resets to **Stage 1** for the next iterative run.

---
*Note: This tool is designed for automated data processing workflows and repository management analysis.*
```