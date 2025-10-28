# Project Report: CodeAgent Vulnerability Scanner

## 1. Introduction

The CodeAgent Vulnerability Scanner is a comprehensive security analysis service designed to identify vulnerabilities in source code. It integrates multiple static analysis tools and leverages AI to provide enhanced feedback, including root cause analysis and suggested code fixes. The scanner can analyze code from GitHub repositories or uploaded ZIP archives, making it a flexible tool for modern development workflows. Its asynchronous architecture, real-time progress updates, and webhook notifications ensure it can be seamlessly integrated into CI/CD pipelines.

## 2. Features

The scanner provides a rich set of features for automated security analysis:

- **Multi-tool Analysis**: Integrates Semgrep, Bandit, and dependency vulnerability scanners for broad coverage.
- **AI-Enhanced Analysis**: Utilizes GPT-4 to provide deep insights into critical and high-severity vulnerabilities, including root cause analysis and security impact assessments.
- **Intelligent Fix Suggestions**: Generates concrete code fixes and security best practice recommendations.
- **Flexible Source Input**: Supports analysis of public GitHub repositories and direct ZIP file uploads.
- **Asynchronous Processing**: Executes scan jobs in the background, allowing for non-blocking API interaction.
- **Real-time Progress Monitoring**: Offers Server-Sent Events (SSE) to track job status live.
- **Webhook Integration**: Notifies external systems upon job completion via HTTP callbacks.
- **Comprehensive and Enhanced Reports**: Delivers normalized JSON reports and AI-enhanced reports with detailed explanations.
- **Dynamic Configuration**: Allows for runtime updates to AI and analyzer settings without service restarts.
- **Dashboard and Metrics**: Provides real-time statistics on scan activity and results.
- **Advanced Filtering**: Enables searching and filtering of reports by severity, tool, repository, and custom labels.
- **RESTful API**: Exposes all functionality through a well-documented REST API with OpenAPI specifications.

## 3. System Architecture

The CodeAgent Vulnerability Scanner is built on a modular, service-oriented architecture. The key components are:

- **API Layer (`api/`)**: A FastAPI application that serves as the entry point for all user interactions. It handles request validation, job submission, and report retrieval.
- **Ingestion Layer (`ingestion/`)**: Responsible for fetching source code from GitHub or processing uploaded ZIP files. It prepares a sanitized workspace for analysis.
- **Analysis Layer (`analyzers/`)**: A pluggable framework that runs various security tools like Semgrep and Bandit. Each tool is a separate runner, making the system extensible.
- **AI Integration (`integration/`)**: This component bridges the scanner with OpenAI's GPT-4. It formats prompts, sends high-severity issues for analysis, and processes the AI-generated feedback.
- **Pipeline Orchestrator (`pipeline/`)**: Manages the lifecycle of a scan job, from queuing and execution to report generation and cleanup.
- **Storage Layer (`storage/`)**: Manages workspaces for running jobs and stores the final JSON reports.

This decoupled architecture ensures that the system is scalable, maintainable, and extensible.

## 4. API Endpoints

The service exposes a comprehensive RESTful API for all its functionalities.

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Checks the health of the service. |
| `/tools` | GET | Lists available security analyzers. |
| `/analyze` | POST | Submits a new scan job. |
| `/jobs/{job_id}` | GET | Retrieves the status of a specific job. |
| `/reports/{job_id}` | GET | Fetches the standard vulnerability report. |
| `/reports/{job_id}/enhanced` | GET | Fetches the AI-enhanced report with detailed fixes. |
| `/config/ai` | GET/PATCH | Manages the AI analysis configuration at runtime. |
| `/dashboard/stats` | GET | Provides dashboard statistics. |
| `/events/{job_id}` | GET | Streams real-time progress updates. |

## 5. AI-Enhanced Analysis

A key innovation of this project is the integration of AI for deeper vulnerability analysis.

- **Process**: After initial scanning, high-severity vulnerabilities are sent to a GPT-4-powered agent. The AI analyzes the code snippet in context and provides a detailed report.
- **Output**: The AI-enhanced report includes:
    - **Root Cause Analysis**: An explanation of why the vulnerability exists.
    - **Suggested Code Fix**: A concrete, ready-to-use code snippet to remediate the issue.
    - **Security Impact**: An assessment of the potential risks.
    - **Best Practices**: Recommendations to prevent similar issues in the future.
- **Cost and Performance Management**: The AI integration is designed with cost-efficiency in mind, featuring configurable severity thresholds, concurrency limits, and timeouts.

## 6. Security Considerations

The scanner itself is designed with security in mind:

- **Sandboxed Execution**: All analysis is performed in isolated, temporary workspaces that are deleted after the job is complete.
- **No Code Execution**: The scanner only performs static analysis and never executes the code it is analyzing.
- **Path Traversal Prevention**: Input from ZIP files is sanitized to prevent path traversal attacks.
- **Resource Limiting**: The system enforces limits on file sizes, file counts, and job timeouts to prevent abuse.

## 7. Conclusion

The CodeAgent Vulnerability Scanner is a powerful and modern tool for automating security reviews. By combining traditional static analysis with cutting-edge AI, it provides developers with actionable insights to improve code security efficiently. Its flexible and scalable architecture makes it suitable for integration into any modern software development lifecycle, helping teams build more secure applications from the ground up.
