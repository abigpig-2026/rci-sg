```yaml
---
name: repo-sync-pipeline
description: A multi-stage automated data processing pipeline that synchronizes GitHub repository metadata with Notion pages. The pipeline orchestrates authentication, data extraction, and API updates in a continuous cycle.
version: 1.0.0
---

# Repo Sync Pipeline

An automated data processing pipeline designed to extract metadata from GitHub repositories and synchronize it with Notion pages. The pipeline operates in a sequential, multi-stage manner, where each stage's output triggers the next. Upon completion, the pipeline resets for the next iteration of data synchronization.

## Usage

To execute the pipeline, ensure you have the necessary credentials and environment variables set:

1.  **Prerequisites:**
    *   GitHub CLI (`gh`) installed and configured.
    *   A valid Notion API key.
    *   Target GitHub repository and Notion page IDs.

2.  **Environment Setup:**
    ```bash
    export NOTION_KEY="your_notion_integration_secret"
    # GitHub CLI will handle its own auth via `gh auth login`
    ```

3.  **Execution:**
    The pipeline is designed to run as a script or within an orchestration tool. Trigger the initial stage (GitHub CLI authentication) to start the automated flow.
    ```bash
    # Initiate the pipeline by starting the first stage
    gh auth login --with-token < your_github_token
    ```
    The subsequent stages will execute automatically based on the output and flow logic.

## Examples

### Full Pipeline Run
This example outlines a complete cycle of the pipeline, synchronizing Pull Request and Issue data to a Notion workspace.

1.  **Stage 1:** Authenticate with GitHub.
    ```bash
    echo $GITHUB_TOKEN | gh auth login --with-token
    ```
    *Outputs authentication status, proceeding to Stage 2.*

2.  **Stage 2:** Update a specific Notion block with initial pipeline status.
    ```bash
    curl -X PATCH "https://api.notion.com/v1/blocks/{notion_page_id}/children" \
      -H "Authorization: Bearer $NOTION_KEY" \
      -H "Notion-Version: 2022-06-28" \
      -H "Content-Type: application/json" \
      --data '{"children":[{"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"Pipeline initiated: Fetching PR data..."}}]}}]}'
    ```
    *Outputs a confirmation string, proceeding to Stage 3.*

3.  **Stage 3:** Fetch merged Pull Requests associated with a specific commit SHA.
    ```bash
    gh pr list --repo owner/repo --search "SHA_HERE" --state merged --json number,title,url
    ```
    *Outputs JSON data of PRs, proceeding to Stage 4.*

4.  **Stage 4:** Update the Notion page properties with the fetched PR summary.
    ```bash
    curl -X PATCH "https://api.notion.com/v1/pages/{notion_page_id}" \
      -H "Authorization: Bearer $NOTION_KEY" \
      -H "Notion-Version: 2022-06-28" \
      -H "Content-Type: application/json" \
      --data '{"properties":{"PR Summary":{"rich_text":[{"type":"text","text":{"content":"3 PRs merged."}}]}}}'
    ```
    *Outputs a confirmation string, proceeding to Stage 5.*

5.  **Stage 5:** Export all repository issues to a local JSON file.
    ```bash
    gh issue list --repo owner/repo --state all --limit 9999 --json number,title,state,labels,assignees > /tmp/issues.json
    ```
    *Outputs a JSON file, proceeding to Stage 6.*

6.  **Stage 6:** Create a new Notion page containing the issue report.
    ```bash
    curl -X POST "https://api.notion.com/v1/pages" \
      -H "Authorization: Bearer $NOTION_KEY" \
      -H "Notion-Version: 2022-06-28" \
      -H "Content-Type: application/json" \
      --data '{"parent":{"database_id":"{notion_database_id}"},"properties":{"Title":{"title":[{"text":{"content":"Issue Report"}}]}}}'
    ```
    *Outputs a confirmation string, proceeding to Stage 7.*

7.  **Stage 7:** Refresh or validate GitHub authentication for the next cycle.
    ```bash
    gh auth status
    ```
    *Outputs auth status. Pipeline cycle completes and resets to Stage 1 for the next iteration.*

## Pipeline Stages

The pipeline consists of seven sequential stages that handle authentication, data extraction, and API communication.

| Stage | Tool | Description | Input | Output | Next Stage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | GitHub CLI | Initiates the pipeline by authenticating with the GitHub API. | CLI flags and tokens (e.g., `--with-token`). | Authentication status, JSON response. | **Notion (Stage 2)** |
| **2** | Notion API | Updates a Notion block to log pipeline initiation status. | Notion Page ID, `NOTION_KEY`. | API result string. | **GitHub CLI (Stage 3)** |
| **3** | GitHub CLI | Queries GitHub for merged Pull Requests filtered by a specific commit SHA. | Repository context, search query (`--search`), JSON output flag. | JSON array of PR data (number, title, url). | **Notion (Stage 4)** |
| **4** | Notion API | Updates the target Notion page's properties with a summary of the fetched PR data. | Notion Page ID, `NOTION_KEY`, structured data from Stage 3. | API result string. | **GitHub CLI (Stage 5)** |
| **5** | GitHub CLI | Exports a comprehensive list of all repository issues (open and closed) to a JSON file. | Repository context, state filter (`--state all`), limit, JSON output flag. | JSON file (`issues.json`). | **Notion (Stage 6)** |
| **6** | Notion API | Creates a new Notion page in a specified database, seeding it with the issue report data. | Notion Database ID, `NOTION_KEY`, page properties. | API result string (new page details). | **GitHub CLI (Stage 7)** |
| **7** | GitHub CLI | Performs a final authentication check, ensuring the session is valid for the next pipeline iteration. | CLI auth commands. | Authentication status. | **Pipeline Resets to Stage 1** |

**Data Flow:** The pipeline is unidirectional. Output from one stage (e.g., a JSON file or confirmation string) serves as the logical trigger or input context for the next stage. The final stage circles back to the beginning, creating a continuous loop for periodic synchronization.
```