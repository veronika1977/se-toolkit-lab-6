"""Tests for agent.py."""

import subprocess
import json
import sys

def test_agent_basic():
    """Test that agent.py returns valid JSON with answer and tool_calls."""
    result = subprocess.run(
        [sys.executable, "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    # Check exit code
    assert result.returncode == 0, f"Agent failed with exit code {result.returncode}"
    
    # Parse JSON from stdout
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        assert False, f"Invalid JSON output: {result.stdout}\nError: {e}"
    
    # Check required fields
    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    
    # Check that tool_calls is an empty list for Task 1
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be a list"
    assert len(output["tool_calls"]) == 0, "'tool_calls' must be empty for Task 1"
    
    print(" Test passed!")

if __name__ == "__main__":
    test_agent_basic()
    print(" All tests passed!")
