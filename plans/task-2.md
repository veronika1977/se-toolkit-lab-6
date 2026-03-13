
### 1. `read_file(path)`
- Reads a file from the project repository
- Security: prevent path traversal (`../`), restrict to project directory
- Returns file contents or error message

### 2. `list_files(path)`
- Lists files and directories at given path
- Security: prevent path traversal, restrict to project directory  
- Returns newline-separated 
1. Send question + tool definitions to LLM
2. If LLM responds with `tool_calls`:
   - Execute each tool
   - Append results as `tool` role messages
   - Repeat step 1 (max 10 iterations)
3. If LLM responds with text (no tool_calls):
   - Extract answer and source
   - Output JSON with tool_calls history

Instruct the LLM to:
- Use `list_files` to explore wiki structure
- Use `read_file` to find answers in relevant files
- Include source in format: `wiki/file.md#section`
- Be thorough and reference specific sections

- Block `../` in all paths
- All paths relative to project root
- Validate file/directory existence
- Prevent access outside project directory

1. Merge conflict question → should call `read_file` on git-workflow.md
2. Wiki files question → should call `list_files` on wiki directory
3. Verify `source` field contains correct path and section
4. Verify `tool_calls` history contains all executed tools with args and results
