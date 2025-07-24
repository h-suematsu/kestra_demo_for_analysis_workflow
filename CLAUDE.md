# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is for testing if Kestra workflow engine can meet the requirements for replacing dbt in an analysis database workflow. It's designed to evaluate Kestra's capability to process analysis results coming from ML models via PubSub, transform them, and store the results.

## Architecture

The project consists of two main workflow components:

1. **Proxy Workflow**: Receives PubSub push events (simulated via REST API in testing) and stores the message content in a KV store
   - Extracts job_id and analysis_type from the messages
   - Stores data with key: <job_id>.<analysis_type>, value: <message>

2. **Analysis Workflow**: Processes data from the KV store when all required analysis types for a job_id are available
   - Triggered by REST API (simulating PubSub)
   - Steps are divided by role with common functionality extracted
   - Output is stored in files

## Development Environment Setup

### Dependencies

```bash
# Install uv (if needed)
brew install uv

# Create virtual environment
uv venv

# Install dependencies
uv sync --all-groups --extra dev
```

### Kestra Server

```bash
# Start Kestra and PostgreSQL
docker compose up -d
```

The Kestra UI is available at http://localhost:8080

## Common Commands

### Running Workflows

To trigger a workflow (example):

```bash
curl -v -X POST -H 'Content-Type: multipart/form-data' \
-F 'message={"job_id": "aaaaaa", "analysis_type": "type_a", "data": {"value": 40}}' \
'http://localhost:8080/api/v1/main/executions/events.demo/proxy_workflow'
```

### Testing

```bash
# Update dependencies
uv sync --all-groups --extra dev

# Run tests
uv run pytest test/
```

### Linting and Formatting

```bash
# Lint check
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```