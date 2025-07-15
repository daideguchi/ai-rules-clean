#!/usr/bin/env python3
"""
🤖 o3 CLI Interface - Direct o3 AI Consultation
==============================================
Simple CLI interface for o3 (o1-preview) AI model consultation

Usage:
    python scripts/o3_cli.py "Your query here"
    python scripts/o3_cli.py --query "Your query here"
"""

import argparse
import asyncio
import os
import sys

from openai import AsyncOpenAI


class O3CLI:
    """Simple CLI interface for o3 AI consultation"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = AsyncOpenAI(api_key=api_key)

    async def query_o3(self, prompt: str, context: str = "") -> str:
        """Query o3 (o1-preview) model"""
        try:
            # Construct message
            if context:
                full_prompt = f"Context: {context}\n\nQuery: {prompt}"
            else:
                full_prompt = prompt

            messages = [{"role": "user", "content": full_prompt}]

            # Call o1-preview as o3 proxy
            response = await self.client.chat.completions.create(
                model="o1-preview", messages=messages, max_completion_tokens=4000
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"❌ o3 Error: {str(e)}"


async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="o3 AI CLI Interface")
    parser.add_argument("query", nargs="?", help="Query for o3")
    parser.add_argument("--query", help="Query for o3 (alternative)")
    parser.add_argument("--context", default="", help="Additional context")

    args = parser.parse_args()

    # Get query from args or positional argument
    query = args.query or args.query
    if not query:
        print("❌ Error: No query provided", file=sys.stderr)
        print("Usage: python scripts/o3_cli.py 'Your query here'", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize CLI
        o3_cli = O3CLI()

        # Execute query
        print("🤖 Consulting o3 AI...", file=sys.stderr)
        result = await o3_cli.query_o3(query, args.context)

        # Output result
        print(result)

    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
