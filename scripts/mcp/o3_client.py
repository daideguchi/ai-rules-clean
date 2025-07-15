#!/usr/bin/env python3
"""
🤖 o3 MCP Client - Direct o3 AI Communication
===========================================
Client for communicating with o3 via MCP server
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

class O3MCPClient:
    """Client for o3 MCP server communication"""

    def __init__(self):
        self.server_path = Path(__file__).parent / "o3_mcp_server.py"

    async def query_o3(self, prompt: str, context: str = "") -> str:
        """Send query to o3 via MCP"""
        try:
            # Create MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "call_o3",
                "params": {
                    "prompt": prompt,
                    "context": context
                }
            }

            # Start MCP server process
            process = await asyncio.create_subprocess_exec(
                "python3", str(self.server_path),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Send request
            request_json = json.dumps(request) + "\n"
            stdout, stderr = await process.communicate(request_json.encode())

            if stderr:
                return f"Error: {stderr.decode()}"

            # Parse response
            response = json.loads(stdout.decode().strip())
            
            if "error" in response:
                return f"o3 Error: {response['error']['message']}"
            
            return response["result"]["content"]

        except Exception as e:
            return f"Client Error: {str(e)}"

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 o3_client.py '<prompt>' ['<context>']")
        sys.exit(1)

    prompt = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else ""

    client = O3MCPClient()
    response = await client.query_o3(prompt, context)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())