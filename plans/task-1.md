
- Использую Qwen Code API на VM (http://10.93.24.245:8000/v1)
- Модель: qwen3-coder-plus

1. read variables from  .env.agent.secret
2. answer from terminal
3. answer LLM API
4. JSON answer
5. stderr

- answer and tool_calls fields are required in the output
-ool_calls is an empty array for this task
- timing 60 sec
- exit code 0
- valid JSON
