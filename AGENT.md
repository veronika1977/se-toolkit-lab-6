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
