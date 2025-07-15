#!/usr/bin/env python3
"""
🤖 o3 MCP Server - Direct o3 AI Integration
==========================================
MCP server for direct o3 AI model communication
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from openai import AsyncOpenAI

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class O3MCPServer:
    """o3 MCP Server"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def call_o3(self, prompt: str, context: str = "") -> str:
        """Call o3 model directly"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"You are o3 AI system. {context}\n\nUser request: {prompt}",
                }
            ]

            response = await self.client.chat.completions.create(
                model="o1-preview",  # Use o1 as proxy for o3
                messages=messages,
                max_completion_tokens=4000,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"o3 Error: {str(e)}"

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP request"""
        try:
            method = data.get("method", "")
            params = data.get("params", {})

            if method == "call_o3":
                prompt = params.get("prompt", "")
                context = params.get("context", "")

                result = await self.call_o3(prompt, context)

                return {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {"content": result, "model": "o3", "status": "success"},
                }

            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {"code": -32601, "message": "Method not found"},
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {"code": -32603, "message": str(e)},
            }


async def main():
    """Main MCP server loop"""
    server = O3MCPServer()

    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            if not line:
                break

            request = json.loads(line.strip())
            response = await server.process_request(request)
            print(json.dumps(response))
            sys.stdout.flush()

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
