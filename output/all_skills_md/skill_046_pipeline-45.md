```yaml
---
name: repo-workflow-analyzer
description: An automated data processing pipeline for analyzing GitHub repository workflows and pull request activity. The pipeline executes a sequence of GitHub CLI and API operations to collect, process, and output repository metadata in a structured format.
version: 1.0.0
---

# Repo Workflow Analyzer

The Repo Workflow Analyzer is an automated, multi-stage data processing pipeline designed to extract and analyze workflow and contribution data from GitHub repositories. It orchestrates a sequence of `github-cli` and `github` operations, automatically passing data between stages to produce consolidated insights. Upon completion of all stages, the pipeline resets and is ready for the next iteration, enabling continuous monitoring or batch processing of multiple repositories.

## Usage

To execute the pipeline, you must have the GitHub CLI (`gh`) installed and authenticated on your system. The pipeline will run the predefined sequence of stages automatically.

**Basic Execution:**
```bash
# The pipeline is triggered as a single unit. Ensure you are in a context where `gh` commands can run.
./repo-workflow-analyzer
```

**Configuration (Optional):**
The pipeline can be configured by setting environment variables prior to execution to target specific repositories or adjust output.
```bash
export GITHUB_OWNER="your-org"
export GITHUB_REPO="your-repo"
export TARGET_PR_NUMBER="55"
./repo-workflow-analyzer
```

## Examples

**Example 1: Analyze a Specific Repository**
This example runs the pipeline for the `octocat/Hello-World` repository.
```bash
export GITHUB_OWNER="octocat"
export GITHUB_REPO="Hello-World"
./repo-workflow-analyzer
```
**Expected Output Flow:**
1.  Authenticates with GitHub.
2.  Lists issues for `octocat/Hello-World`.
3.  Searches for merged pull requests.
4.  Fetches details for a specific pull request (e.g., #55).
5.  Final authentication check.
6.  Outputs a summary file (`single-file.tar.gz`) containing the collected data.

**Example 2: Using Pipeline Output**
The primary structured output is a JSON file which can be processed further.
```bash
./repo-workflow-analyzer
tar -xzf output/single-file.tar.gz
cat extracted_data.json | jq '.'
```

## Pipeline Stages

The pipeline consists of five sequential stages. Data and state are automatically passed from one stage to the next.

### Stage 1: Authentication & Session Initiation
*   **Tool:** `github-cli`
*   **Command:** `gh auth login`
*   **Description:** Initializes the pipeline by establishing an authenticated session with the GitHub API. This ensures all subsequent commands have the necessary permissions to access repository data. The stage accepts a wide array of potential flags for flexible authentication (e.g., `--with-token`, `--hostname`).
*   **Inputs:** Authentication parameters (e.g., token, hostname).
*   **Outputs:** An active authenticated session. Prepares for repository operations.
*   **Next Stage:** Flows to `github` (Stage 2).

### Stage 2: Repository Issue Listing
*   **Tool:** `github`
*   **Command:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Description:** Queries the target GitHub repository to fetch a list of open issues. The output is formatted using `jq` to provide a concise list of issue numbers and titles. This stage demonstrates basic repository interrogation.
*   **Inputs:** Repository owner and name (e.g., `--repo octocat/Hello-World`).
*   **Outputs:** A formatted string list of issues (e.g., `"123: Bug report", "124: Feature request"`).
*   **Next Stage:** Flows to `github-cli` (Stage 3).

### Stage 3: Merged Pull Request Search
*   **Tool:** `github-cli`
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Searches the repository's pull requests for those that have been merged, potentially filtered by a commit SHA. It outputs structured JSON data containing the PR number, title, and URL. This stage focuses on identifying completed contributions.
*   **Inputs:** Search query (`--search`), state filter (`--state merged`).
*   **Outputs:** JSON array of pull request objects.
*   **Next Stage:** Flows to `github` (Stage 4).

### Stage 4: Detailed Pull Request Inspection
*   **Tool:** `github`
*   **Command:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Description:** Makes a direct API call to fetch detailed metadata for a specific pull request (by default, number 55). It extracts key fields like the title, current state, and the author's login. This stage performs deep inspection of individual workflow items.
*   **Inputs:** API path (`repos/owner/repo/pulls/55`).
*   **Outputs:** A string containing the pull request title, state, and author.
*   **Next Stage:** Flows to `github-cli` (Stage 5).

### Stage 5: Session Verification & Output Finalization
*   **Tool:** `github-cli`
*   **Command:** `gh auth login`
*   **Description:** Re-verifies or refreshes the authentication session. This stage ensures the integrity of the session after a series of operations and acts as the final step before pipeline completion. It consolidates any logs or debug output from previous stages.
*   **Inputs:** Session verification parameters.
*   **Outputs:** Final pipeline artifacts, including a consolidated data archive (`single-file.tar.gz`) and optional debug logs showing full HTTP traces.
*   **Next Stage:** The pipeline loops back to Stage 1, ready for the next execution cycle.

---
*Note: This tool is designed for automated data processing and analysis workflows. Ensure you have appropriate authorization to access any target repositories.*
```