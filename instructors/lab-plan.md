# Lab plan — Build Your Own Agent

**Topic:** Agent loop, LLM tool calling, CLI development, course review
**Date:** 2026-03-12

## Main goals

- Demystify the agent loop by building one from scratch.
- Reinforce understanding of all course material (labs 1-6) through a wiki-based agent and evaluation benchmark.
- Teach LLM API integration and tool calling as a transferable skill.

## Learning outcomes

By the end of this lab, students should be able to:

- [Understand] Explain how an agentic loop works: user input → LLM → tool call → execute → feed result → repeat until final answer.
- [Apply] Integrate with an LLM API using the OpenAI-compatible chat completions format with tool/function calling.
- [Apply] Implement tools that read files, list directories, and query HTTP APIs, then register them as function-calling schemas.
- [Apply] Build a CLI that accepts structured input and produces structured output (JSON).
- [Analyze] Debug agent behavior by examining tool call traces, identifying prompt issues, and fixing tool implementations.
- [Evaluate] Assess agent quality against a benchmark, iterating on prompts and tools to improve pass rate.

In simple words:

> 1. I can explain how an agent loop works — prompt, tool call, execute, feed back, repeat.
> 2. I can call an LLM API with tool definitions and handle structured responses.
> 3. I can build tools that read files, list directories, and query APIs, and wire them into an agent.
> 4. I can build a CLI that takes a question and outputs a JSON answer.
> 5. I can debug why my agent gives wrong answers by tracing tool calls and fixing prompts.
> 6. I can iterate on my agent until it passes a benchmark, improving prompts and tools along the way.

## Lab story

You have a running Learning Management Service from the previous lab — a backend, a database full of analytics data, and a frontend dashboard. Your project has a wiki full of documentation that nobody reads. You will build a CLI agent that reads the docs for you, answers questions about the course, and then connects to the live system to do something actually useful — analyze logs and diagnose bugs.

A senior engineer explains the assignment:

> 1. Build an agent that reads the project wiki and answers questions by finding the right section — the documentation agent.
> 2. Connect the agent to your live system so it can query the API, inspect the codebase, and answer questions about the actual deployment — the system agent.
> 3. Polish the agent until it passes the full evaluation benchmark, including diagnosing bugs from application logs — the reliable agent.

## Required tasks

### Task 1 — The Documentation Agent

**Purpose:**

Build an agent that answers questions by navigating the project wiki, finding the relevant section, and providing the answer — learning the agentic loop, tool calling, and CLI design in the process.

**Summary:**

Students create `agent.py` in the project root. The CLI takes a question as a command-line argument and outputs JSON with three fields: `answer` (the text answer), `source` (the wiki section reference), and `tool_calls` (the tools used). An agent is a program that uses an LLM with tools to accomplish tasks. The agent must use `read_file` and `list_files` tools to navigate the `wiki/` directory, find the section that answers the question, and return both the answer and the source reference.

Students choose an LLM provider (OpenRouter recommended), set up tool calling (verified during setup), and implement the agentic loop: call the LLM with tool definitions, execute any tool calls, feed results back, repeat until the LLM produces a final answer. The wiki section makes the output deterministic — students can verify their own answers by reading the section.

Students write a plan before coding, document their architecture in AGENT.md, and create regression tests. The benchmark tests ~15 wiki questions with deterministic expected sections.

**Acceptance criteria:**

- `agent.py` returns JSON with `answer`, `source`, and `tool_calls` fields.
- The agent uses `read_file` and `list_files` tools to navigate the wiki.
- The `source` field correctly identifies the wiki section that answers the question.
- The benchmark passes all wiki questions locally.
- PR is approved and merged, closing the linked issue.

---

### Task 2 — The System Agent

**Purpose:**

Connect the agent to the live system so it can query the API, inspect source code, and answer questions about the actual deployment.

**Summary:**

Students add a `query_api` tool that makes HTTP requests to the deployed backend, authenticating with `LMS_API_KEY`. The agent can now answer two kinds of questions: static system facts (framework, ports, ORM — deterministic, baked into code) and data-dependent queries (item count, scores — verified by range checks).

Students extend the system prompt to help the LLM decide when to use wiki tools vs system tools. They update documentation and tests to cover the new tool. The benchmark adds ~11 system questions on top of the existing wiki questions.

**Acceptance criteria:**

- The `query_api` tool is implemented and authenticates with the backend.
- The agent answers static system questions correctly (framework, ports, status codes).
- The agent answers data-dependent questions with plausible values.
- The benchmark passes all wiki and system questions locally.
- PR is approved and merged, closing the linked issue.

---

### Task 3 — Pass the Benchmark

**Purpose:**

Iterate on the agent until it passes the full evaluation benchmark, including hidden questions that require chaining tools to diagnose bugs from application logs.

**Summary:**

Students run `python run_eval.py` to test against local questions, then submit to the autochecker bot which tests additional hidden questions. Hidden questions include multi-step challenges: find an error in the application logs, trace it to the source file, and suggest a fix. These require chaining tools (query logs → read source → reason about fix).

The backend contains 2-3 planted non-critical bugs that produce log entries. Students iterate on their agent until it can find, trace, and diagnose these issues. Common improvements include better system prompts, improved tool descriptions, and handling of multi-step reasoning.

Students document their iteration process, lessons learned, and final evaluation score in AGENT.md.

**Acceptance criteria:**

- `run_eval.py` passes all local questions.
- The autochecker bot benchmark passes at least 75%.
- The agent successfully diagnoses at least one planted bug from logs.
- AGENT.md documents final architecture and lessons learned.
- PR is approved and merged, closing the linked issue.

---

## Optional task

### Task 1 — Advanced Agent Features

**Purpose:**

Extend the agent with advanced capabilities that improve reliability, expand coverage, or demonstrate deeper understanding of agent design.

**Summary:**

Students choose one or more extensions: retry logic with exponential backoff for rate-limited LLM APIs, a caching layer that avoids re-calling tools for repeated arguments, a `query_db` tool that runs read-only SQL queries against PostgreSQL directly, or multi-step reasoning where the agent plans before executing tools.

Students document their chosen extension in a plan, implement it, and write tests that demonstrate the improvement. The extension should measurably improve the agent.

**Acceptance criteria:**

- At least one extension is implemented and documented.
- Tests demonstrate the extension works correctly.
- AGENT.md is updated to describe the extension.
- PR is approved and merged, closing the linked issue.
