# Agent Documentation

## Overview
This agent is a CLI tool that connects to OpenRouter.ai LLM API and returns structured JSON responses. It serves as the foundation for Task 1 of the lab.

## Setup

### Prerequisites
- Python 3.14+
- uv package manager

### Installation
```bash
# Install dependencies
uv add openai python-dotenv httpx

# Configure environment
cp .env.agent.example .env.agent.secret
# Edit .env.agent.secret with your API credentials
# System Agent - Task 3

## Architecture
The System Agent extends the Task 2 agent with a `query_api` tool that communicates with the live backend API. The agent uses environment variables for configuration:
- `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL` - for Qwen API access
- `LMS_API_KEY` - for backend authentication
- `AGENT_API_BASE_URL` - backend URL (default: http://localhost:42002)

## Tools
1. **list_files** - Explore directories
2. **read_file** - Read documentation and source code
3. **query_api** - Send HTTP requests to the backend

## Tool Selection Logic
The system prompt guides the LLM to choose appropriate tools:
- `read_file` for documentation and code analysis
- `query_api` for live data (item counts, status codes, analytics)
- Combined usage for bug diagnosis (API error + source code)

## Benchmark Results
Current score: 6/10 local questions passing. The agent successfully handles:
- Wiki documentation questions
- Framework identification
- Database item count via API
- HTTP status code testing

## Challenges & Solutions
- **Database connection**: Fixed by configuring app to listen on all interfaces
- **Caddy proxy issues**: Used direct app access on port 42001 via SSH tunnel
- **Empty tables**: Populated via ETL sync and manual data insertion

## Lessons Learned
1. Always verify network connectivity between containers
2. Use SSH tunnels for secure local-to-VM communication
3. Log API errors for better debugging
4. Combine multiple tools for complex questions
