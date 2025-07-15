#!/usr/bin/env python3
"""
Claude Code GitHub Actions Handler
AI-powered GitHub issue and PR processing with Claude integration
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests

try:
    import anthropic
except ImportError:
    print("Installing anthropic package...")
    os.system("pip install anthropic")
    import anthropic


class ClaudeGitHubHandler:
    def __init__(self):
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repository = os.environ.get("GITHUB_REPOSITORY", "")

        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")

        self.claude = anthropic.Anthropic(api_key=self.anthropic_key)
        self.github_api_base = "https://api.github.com"

        # Load project configuration
        self.project_config = self._load_project_config()

    def _load_project_config(self) -> Dict[str, Any]:
        """Load CLAUDE.md project configuration"""
        try:
            claude_md_path = Path("CLAUDE.md")
            if claude_md_path.exists():
                with open(claude_md_path, encoding="utf-8") as f:
                    content = f.read()

                return {
                    "has_claude_config": True,
                    "content": content,
                    "is_ai_safety_template": "AI安全ガバナンス" in content,
                    "has_president_system": "PRESIDENT宣言" in content,
                    "has_tmux_config": "tmux設定" in content,
                }
        except Exception as e:
            print(f"Warning: Could not load CLAUDE.md: {e}")

        return {"has_claude_config": False}

    def _github_api_request(
        self, method: str, endpoint: str, data: Dict = None
    ) -> Dict:
        """Make GitHub API request"""
        url = f"{self.github_api_base}/repos/{self.repository}/{endpoint}"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    def _extract_claude_mentions(self, text: str) -> List[str]:
        """Extract @claude mentions and associated requests"""
        import re

        # Pattern to match @claude mentions and following text
        claude_pattern = r"@claude\s+([^\n@]+(?:\n(?!@)[^\n@]*)*)"
        matches = re.findall(claude_pattern, text, re.MULTILINE | re.IGNORECASE)

        return [match.strip() for match in matches if match.strip()]

    def _create_claude_context(self, request: str, issue_data: Dict) -> str:
        """Create context for Claude processing"""
        context_parts = [
            "# Claude Code GitHub Actions Context",
            "",
            f"## Project: {self.repository}",
            f"## Request: {request}",
            "",
            "## Issue/PR Information:",
            f"- Title: {issue_data.get('title', 'N/A')}",
            f"- Author: {issue_data.get('user', {}).get('login', 'N/A')}",
            f"- Created: {issue_data.get('created_at', 'N/A')}",
            f"- Labels: {', '.join([label['name'] for label in issue_data.get('labels', [])])}",
            "",
            "## Issue/PR Description:",
            issue_data.get("body", "No description provided"),
            "",
        ]

        # Add project-specific context
        if self.project_config.get("has_claude_config"):
            context_parts.extend(
                [
                    "## Project Configuration (CLAUDE.md):",
                    "This project has Claude configuration. Key features:",
                    "",
                ]
            )

            if self.project_config.get("is_ai_safety_template"):
                context_parts.append("- ✅ AI Safety Governance Template")
            if self.project_config.get("has_president_system"):
                context_parts.append("- ✅ PRESIDENT Declaration System")
            if self.project_config.get("has_tmux_config"):
                context_parts.append("- ✅ tmux Worker Control System")

            context_parts.extend(
                ["", "Follow the project's established patterns and standards.", ""]
            )

        return "\n".join(context_parts)

    def _process_with_claude(self, context: str) -> str:
        """Process request with Claude"""
        try:
            system_message = """You are Claude, an AI assistant integrated with GitHub Actions.
            You help with code analysis, issue resolution, and pull request creation.

            Guidelines:
            1. Provide actionable, specific responses
            2. Follow the project's coding standards and patterns
            3. Suggest concrete implementation steps
            4. Be concise but comprehensive
            5. If creating code, ensure it follows the project structure
            6. For AI Safety Governance projects, respect PRESIDENT declaration systems and tmux configurations

            Response format:
            - Use markdown formatting
            - Include code blocks when relevant
            - Provide step-by-step instructions when applicable
            - End with a summary of suggested actions"""

            message = self.claude.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.1,
                system=system_message,
                messages=[{"role": "user", "content": context}],
            )

            return message.content[0].text

        except Exception as e:
            return f"❌ Claude processing failed: {str(e)}\n\nPlease try again or contact support."

    def _post_github_comment(self, issue_number: int, comment_body: str):
        """Post comment to GitHub issue/PR"""
        try:
            comment_data = {
                "body": f"## 🤖 Claude Code Response\n\n{comment_body}\n\n---\n*Powered by Claude Code GitHub Actions*"
            }

            self._github_api_request(
                "POST", f"issues/{issue_number}/comments", comment_data
            )
            print(f"✅ Posted Claude response to issue #{issue_number}")

        except Exception as e:
            print(f"❌ Failed to post comment: {e}")

    def handle_issue_event(self, issue_number: int, comment_body: str):
        """Handle GitHub issue or PR event"""
        try:
            print(f"Processing issue #{issue_number}")

            # Get issue data
            issue_data = self._github_api_request("GET", f"issues/{issue_number}")

            # Extract Claude mentions
            claude_requests = self._extract_claude_mentions(comment_body)

            if not claude_requests:
                print("No @claude mentions found")
                return

            print(f"Found {len(claude_requests)} Claude request(s)")

            # Process each request
            for i, request in enumerate(claude_requests):
                print(f"Processing request {i + 1}: {request[:50]}...")

                # Create context and process with Claude
                context = self._create_claude_context(request, issue_data)
                response = self._process_with_claude(context)

                # Post response
                self._post_github_comment(issue_number, response)

            print("✅ All Claude requests processed successfully")

        except Exception as e:
            print(f"❌ Error handling issue event: {e}")
            # Post error comment
            error_comment = f"❌ **Claude Processing Error**\n\n```\n{str(e)}\n```\n\nPlease check the action logs for more details."
            try:
                self._post_github_comment(issue_number, error_comment)
            except Exception:
                pass


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Claude Code GitHub Actions Handler")
    parser.add_argument("--event-type", required=True, help="GitHub event type")
    parser.add_argument("--repository", required=True, help="Repository name")
    parser.add_argument("--issue-number", type=int, help="Issue/PR number")
    parser.add_argument("--comment-body", required=True, help="Comment body text")

    args = parser.parse_args()

    try:
        print("🚀 Claude Code GitHub Actions Handler starting...")
        print(f"📋 Event: {args.event_type}")
        print(f"📁 Repository: {args.repository}")
        print(f"🔢 Issue: #{args.issue_number}")

        # Initialize handler
        handler = ClaudeGitHubHandler()

        # Process the event
        if args.issue_number:
            handler.handle_issue_event(args.issue_number, args.comment_body)
        else:
            print("⚠️ No issue number provided, skipping processing")

        print("✅ Claude Code processing completed")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
