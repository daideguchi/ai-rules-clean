#!/usr/bin/env python3
"""
💎 Gemini MCP Server - Direct Gemini AI Integration
==================================================
MCP server for direct Gemini AI model communication
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

import google.generativeai as genai

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class GeminiMCPServer:
    """Gemini MCP Server"""

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def call_gemini(self, prompt: str, context: str = "") -> str:
        """Call Gemini model directly"""
        try:
            full_prompt = f"""You are Gemini AI system. {context}

User request: {prompt}

Please provide your analysis as Gemini AI."""

            response = await asyncio.get_event_loop().run_in_executor(
                None, self.model.generate_content, full_prompt
            )

            return response.text

        except Exception as e:
            return f"Gemini Error: {str(e)}"

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP request"""
        try:
            method = data.get("method", "")
            params = data.get("params", {})

            if method == "call_gemini":
                prompt = params.get("prompt", "")
                context = params.get("context", "")

                result = await self.call_gemini(prompt, context)

                return {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {
                        "content": result,
                        "model": "gemini",
                        "status": "success",
                    },
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
    server = GeminiMCPServer()

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
