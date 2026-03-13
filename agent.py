#!/usr/bin/env python3
"""
Documentation Agent with tools for reading wiki files.
Task 2 implementation with agentic loop and file tools.
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# Load environment variables
load_dotenv('.env.agent.secret')

# Project root directory - for security
PROJECT_ROOT = Path(__file__).parent.absolute()

# Maximum number of tool calls per question
MAX_TOOL_CALLS = 10

def read_file(path: str) -> str:
    """
    Read a file from the project repository.
    
    Security: prevents directory traversal, restricts to project directory.
    
    Args:
        path: Relative path from project root (e.g., 'wiki/git-workflow.md')
        
    Returns:
        File contents as string, or error message if file cannot be read
    """
    try:
        # Security: prevent directory traversal
        clean_path = path.replace('\\', '/').strip()
        if '..' in clean_path.split('/'):
            return "Error: Directory traversal not allowed"
        
        full_path = PROJECT_ROOT / clean_path
        
        # Security: ensure path is within project
        if not str(full_path).startswith(str(PROJECT_ROOT)):
            return "Error: Access outside project directory"
        
        if not full_path.exists():
            return f"Error: File {path} not found"
        
        if not full_path.is_file():
            return f"Error: {path} is not a file"
        
        # Read file with UTF-8 encoding
        return full_path.read_text(encoding='utf-8')
    
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(path: str = ".") -> str:
    """
    List files and directories at a given path.
    
    Security: prevents directory traversal, restricts to project directory.
    
    Args:
        path: Relative directory path from project root (default: ".")
        
    Returns:
        Newline-separated listing of entries, with "/" suffix for directories
    """
    try:
        # Security: prevent directory traversal
        clean_path = path.replace('\\', '/').strip()
        if '..' in clean_path.split('/'):
            return "Error: Directory traversal not allowed"
        
        full_path = PROJECT_ROOT / clean_path
        
        # Security: ensure path is within project
        if not str(full_path).startswith(str(PROJECT_ROOT)):
            return "Error: Access outside project directory"
        
        if not full_path.exists():
            return f"Error: Path {path} not found"
        
        if not full_path.is_dir():
            return f"Error: {path} is not a directory"
        
        # List all entries, mark directories with "/"
        entries = []
        for entry in full_path.iterdir():
            suffix = "/" if entry.is_dir() else ""
            entries.append(f"{entry.name}{suffix}")
        
        return "\n".join(sorted(entries))
    
    except Exception as e:
        return f"Error listing files: {str(e)}"

# Tool definitions for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the project repository. Use this to find answers in wiki documentation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file from project root (e.g., 'wiki/git-workflow.md')"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given path. Use this to explore the wiki structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path (default: '.' for project root)",
                        "default": "."
                    }
                },
                "required": []
            }
        }
    }
]

def execute_tool(tool_call):
    """
    Execute a tool call and return the result in OpenAI format.
    
    Args:
        tool_call: OpenAI tool call object
        
    Returns:
        Dictionary with role="tool", tool_call_id, and content (result)
    """
    tool_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    if tool_name == "read_file":
        result = read_file(args.get("path", ""))
    elif tool_name == "list_files":
        result = list_files(args.get("path", "."))
    else:
        result = f"Error: Unknown tool {tool_name}"
    
    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result
    }

def main():
    """Main entry point with agentic loop for tool-calling."""
    start_time = time.time()
    
    # Debug output to stderr
    print("🚀 Starting Documentation Agent...", file=sys.stderr)
    
    # Check command line argument
    if len(sys.argv) < 2:
        print("❌ Error: No question provided", file=sys.stderr)
        print("Usage: uv run agent.py 'Your question here'", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    print(f"📝 Question: {question}", file=sys.stderr)
    
    # Get LLM configuration
    api_key = os.getenv('LLM_API_KEY')
    api_base = os.getenv('LLM_API_BASE')
    model = os.getenv('LLM_MODEL')
    
    # Validate configuration
    if not api_key or not api_base or not model:
        print("❌ Error: LLM credentials not set in .env.agent.secret", file=sys.stderr)
        print("   Required: LLM_API_KEY, LLM_API_BASE, LLM_MODEL", file=sys.stderr)
        sys.exit(1)
    
    print(f"🤖 Using model: {model}", file=sys.stderr)
    print(f"🔗 API Base: {api_base}", file=sys.stderr)
    
    try:
        # Initialize OpenAI client with timeout
        client = OpenAI(
            api_key=api_key,
            base_url=api_base,
            http_client=httpx.Client(timeout=30.0)
        )
        
        # Initialize messages with system prompt
        messages = [
            {
                "role": "system",
                "content": """You are a Documentation Agent for a software engineering toolkit.
Your task is to answer questions using the project wiki.

Available tools:
- list_files(path): Explore wiki structure
- read_file(path): Read wiki files

Instructions:
1. First, use list_files to see what wiki files exist
2. Then use read_file on relevant files to find answers
3. Always include the source file and section in your answer
4. Format source as: wiki/filename.md#section-name

Example source: wiki/git-workflow.md#resolving-merge-conflicts

Answer questions thoroughly based on the wiki content.
If you can't find the answer, say so and suggest where to look."""
            },
            {"role": "user", "content": question}
        ]
        
        # Store all tool calls for output
        all_tool_calls = []
        tool_call_count = 0
        answer = None
        source = None
        
        # Agentic loop - max MAX_TOOL_CALLS iterations
        while tool_call_count < MAX_TOOL_CALLS:
            print(f"🔄 Agentic loop iteration {tool_call_count + 1}", file=sys.stderr)
            
            # Call LLM with tools
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Check if there are tool calls
            if not message.tool_calls:
                # No tool calls - this is the final answer
                print("✅ No more tool calls, generating final answer", file=sys.stderr)
                answer = message.content
                
                # Try to extract source from answer using regex
                source_match = re.search(r'(wiki/[^#\s]+\.md#[^\s\)]+)', answer)
                if source_match:
                    source = source_match.group(1)
                    print(f"📌 Found source: {source}", file=sys.stderr)
                else:
                    source = "wiki/README.md"
                    print("📌 No source found, using default", file=sys.stderr)
                
                break
            
            # Process tool calls
            print(f"🔧 Tool calls: {len(message.tool_calls)}", file=sys.stderr)
            
            # Add assistant message with tool calls to history
            messages.append(message)
            
            # Execute each tool call
            for tool_call in message.tool_calls:
                print(f"  ⚙️  Executing: {tool_call.function.name}({tool_call.function.arguments})", file=sys.stderr)
                
                # Execute tool
                tool_result = execute_tool(tool_call)
                messages.append(tool_result)
                
                # Store for output
                all_tool_calls.append({
                    "tool": tool_call.function.name,
                    "args": json.loads(tool_call.function.arguments),
                    "result": tool_result["content"]
                })
                
                tool_call_count += 1
                
                # Check if we've hit the limit
                if tool_call_count >= MAX_TOOL_CALLS:
                    print(f"⚠️  Reached maximum tool calls ({MAX_TOOL_CALLS})", file=sys.stderr)
                    break
        
        # If we exited loop without answer (max calls reached), get final response
        if answer is None:
            print("⚠️  Max tool calls reached, getting final answer", file=sys.stderr)
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            answer = response.choices[0].message.content
            source = "wiki/README.md (max calls reached)"
        
        # Prepare final output
        result = {
            "answer": answer,
            "source": source,
            "tool_calls": all_tool_calls
        }
        
        # Check total time
        elapsed = time.time() - start_time
        print(f"⏱️  Total time: {elapsed:.2f}s", file=sys.stderr)
        
        if elapsed > 60:
            print(f"⚠️  Warning: Response time {elapsed:.2f}s exceeds 60s limit", file=sys.stderr)
        
        # Output JSON to stdout (only JSON, no debug)
        print(json.dumps(result, ensure_ascii=False))
        
    except httpx.TimeoutException:
        print("❌ Error: LLM request timeout", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
