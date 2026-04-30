```yaml
---
name: browser-setup-pipeline
description: A multi-stage automated pipeline for browser environment setup and validation.
version: 1.0.0
---

# Browser Setup Pipeline

This skill implements an automated, multi-stage data processing pipeline designed to set up and validate a browser automation environment. The pipeline executes a sequence of `agent-browser` operations, where the output of each stage automatically flows as input to the next. Upon completion of the final stage, the pipeline can be configured to restart for continuous iteration or validation cycles.

## Usage

The pipeline is invoked as a single skill. It requires no initial input parameters as it manages its own internal state and data flow between stages.

```bash
# Execute the full pipeline
skill run browser-setup-pipeline
```

The pipeline will execute sequentially:
1.  **Stage 1:** Initializes a browser session and navigates to a target URL.
2.  **Stage 2:** Installs necessary browser dependencies (including system-level packages for Linux environments).
3.  **Stage 3:** Repeats dependency installation for robustness and verification.
4.  **Stage 4:** Downloads the core browser binary (e.g., Chromium).
5.  **Stage 5:** Validates the setup by opening the target URL in the newly configured environment.

Each stage produces a `result` string (e.g., status messages, page content, installation logs) which is passed to the subsequent stage. The final output is the consolidated result from Stage 5.

## Examples

### Example 1: Basic Execution
Run the complete setup and validation pipeline.

```bash
$ skill run browser-setup-pipeline
[INFO] Starting Browser Setup Pipeline v1.0.0
[INFO] Stage 1: Opening initial session to https://example.com... Success.
[INFO] Stage 2: Installing browser with system dependencies... Success.
[INFO] Stage 3: Verifying dependency installation... Success.
[INFO] Stage 4: Downloading Chromium binary... Success.
[INFO] Stage 5: Final validation via https://example.com... Success.
[INFO] Pipeline completed. Environment ready.
```

### Example 2: Pipeline Output
The final output is a string summarizing the pipeline's execution.

```
Pipeline Execution Summary:
- Stage 1: Loaded page 'Example Domain' from https://example.com.
- Stage 2: Installed libx11-xcb1, libxcomposite1, libxcursor1, libxdamage1, libxi6, libxtst6, libnss3, libcups2, libxss1, libxrandr2, libasound2, libatk1.0-0, libatk-bridge2.0-0, libpangocairo-1.0-0, libgtk-3-0.
- Stage 3: Dependency verification passed. All packages present.
- Stage 4: Downloaded Chromium v121.0.6167.85 to /usr/local/bin.
- Stage 5: Validation successful. Page 'Example Domain' loaded in new browser context.
```

## Pipeline Stages

### Stage 1: Session Initialization
*   **Agent:** `agent-browser`
*   **Command:** `open https://example.com`
*   **Input:** Accepts various parameters (`url`, `session`, `load`, etc.). For this pipeline, the `url` parameter is pre-configured.
*   **Output:** `result` (string) - Contains the initial page content or session status.
*   **Purpose:** Establishes a baseline browser session and confirms network/URL accessibility.
*   **Next Stage:** Output flows to **Stage 2**.

### Stage 2: Dependency Installation (System)
*   **Agent:** `agent-browser`
*   **Command:** `install --with-deps`
*   **Input:** Receives the `result` from Stage 1. Utilizes the `--with-deps` flag.
*   **Output:** `result` (string) - Log of installed system and browser dependencies.
*   **Purpose:** Installs all required libraries and system packages for the browser to function on a Linux environment.
*   **Next Stage:** Output flows to **Stage 3**.

### Stage 3: Dependency Verification
*   **Agent:** `agent-browser`
*   **Command:** `install --with-deps`
*   **Input:** Receives the installation log from Stage 2.
*   **Output:** `result` (string) - Confirmation log from the second installation pass.
*   **Purpose:** Ensures dependency installation was complete and successful, acting as a verification step.
*   **Next Stage:** Output flows to **Stage 4**.

### Stage 4: Browser Binary Acquisition
*   **Agent:** `agent-browser`
*   **Command:** `install`
*   **Input:** Receives the verification result from Stage 3.
*   **Output:** `result` (string) - Log of the Chromium download and setup process.
*   **Purpose:** Downloads the core browser executable (Chromium) after dependencies are confirmed.
*   **Next Stage:** Output flows to **Stage 5**.

### Stage 5: Environment Validation
*   **Agent:** `agent-browser`
*   **Command:** `open https://example.com`
*   **Input:** Receives the browser setup log from Stage 4.
*   **Output:** `result` (string) - The final page content and validation status.
*   **Purpose:** Tests the fully configured browser environment by loading the target URL, confirming the entire pipeline's success.
*   **Next Stage:** Pipeline completes. Can be looped back to Stage 1 for iterative runs.

---
*Note: This tool is designed for security research and red team testing to automate environment preparation for browser-based assessments.*
```