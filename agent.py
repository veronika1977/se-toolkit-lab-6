#!/usr/bin/env python3
import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('.env.agent.secret')

def main():
    if len(sys.argv) < 2:
        print("❌ Error: No question provided", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    
    api_key = os.getenv('LLM_API_KEY')
    api_base = os.getenv('LLM_API_BASE')
    model = os.getenv('LLM_MODEL')
    
    if not api_key or not api_base:
        print("❌ Error: LLM credentials not set", file=sys.stderr)
        sys.exit(1)
    
    try:
        client = OpenAI(api_key=api_key, base_url=api_base)
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}]
        )
        
        result = {
            "answer": response.choices[0].message.content,
            "tool_calls": []
        }
        print(json.dumps(result))
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
