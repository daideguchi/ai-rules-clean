#!/usr/bin/env python3
"""
Claude Code PR Reviewer
Automated PR review with Claude integration for AI Safety Governance projects
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import requests

try:
    import anthropic
except ImportError:
    os.system("pip install anthropic")
    import anthropic


class ClaudePRReviewer:
    def __init__(self):
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repository = os.environ.get("GITHUB_REPOSITORY", "")

        if not self.anthropic_key or not self.github_token:
            raise ValueError("ANTHROPIC_API_KEY and GITHUB_TOKEN are required")

        self.claude = anthropic.Anthropic(api_key=self.anthropic_key)
        self.github_api_base = "https://api.github.com"

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

        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def _get_pr_diff(self, base_sha: str, head_sha: str) -> str:
        """Get PR diff using git"""
        try:
            result = subprocess.run(
                ["git", "diff", f"{base_sha}..{head_sha}"],
                capture_output=True,
                text=True,
            )
            return result.stdout
        except Exception as e:
            print(f"Warning: Could not get git diff: {e}")
            return ""

    def _get_changed_files(self, pr_number: int) -> List[Dict]:
        """Get list of changed files in PR"""
        try:
            return self._github_api_request("GET", f"pulls/{pr_number}/files")
        except Exception as e:
            print(f"Warning: Could not get changed files: {e}")
            return []

    def _analyze_with_claude(
        self, pr_data: Dict, diff_content: str, changed_files: List[Dict]
    ) -> str:
        """Analyze PR with Claude"""

        # Check if this is an AI Safety Governance project
        is_ai_safety_project = Path("CLAUDE.md").exists()
        has_president_system = False
        has_tmux_config = False

        if is_ai_safety_project:
            try:
                with open("CLAUDE.md") as f:
                    claude_content = f.read()
                    has_president_system = "PRESIDENT宣言" in claude_content
                    has_tmux_config = "tmux設定" in claude_content
            except Exception:
                pass

        # Create specialized system message for AI Safety projects
        if is_ai_safety_project:
            system_message = """You are Claude, reviewing a pull request for an AI Safety Governance project.

            This project has specific requirements:
            1. PRESIDENT declaration system integrity
            2. tmux worker control system standards
            3. Hook system functionality
            4. Memory inheritance system
            5. Constitutional AI compliance
            6. Security and safety standards

            Focus your review on:
            - Security implications of changes
            - Compliance with established patterns
            - Hook system integrity
            - PRESIDENT declaration system preservation
            - tmux configuration standards
            - Memory system consistency
            - Code quality and maintainability

            Provide specific, actionable feedback."""
        else:
            system_message = """You are Claude, providing automated code review.

            Focus on:
            - Code quality and best practices
            - Security considerations
            - Performance implications
            - Maintainability
            - Testing coverage
            - Documentation

            Provide constructive, specific feedback."""

        # Prepare context
        context_parts = [
            f"# Pull Request Review: {pr_data['title']}",
            "",
            f"**Author**: {pr_data['user']['login']}",
            f"**Target Branch**: {pr_data['base']['ref']}",
            f"**Source Branch**: {pr_data['head']['ref']}",
            "",
            "## PR Description:",
            pr_data.get("body", "No description provided"),
            "",
            "## Changed Files:",
        ]

        for file in changed_files[:10]:  # Limit to first 10 files
            context_parts.append(
                f"- `{file['filename']}` (+{file['additions']} -{file['deletions']})"
            )

        if len(changed_files) > 10:
            context_parts.append(f"- ... and {len(changed_files) - 10} more files")

        context_parts.extend(
            [
                "",
                "## Code Diff (First 3000 characters):",
                "```diff",
                diff_content[:3000],
                "```",
                "",
            ]
        )

        if is_ai_safety_project:
            context_parts.extend(
                [
                    "## AI Safety Project Considerations:",
                    f"- PRESIDENT System: {'✅' if has_president_system else '❌'}",
                    f"- tmux Config: {'✅' if has_tmux_config else '❌'}",
                    "- Review for safety, security, and system integrity",
                    "",
                ]
            )

        context = "\n".join(context_parts)

        try:
            message = self.claude.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.1,
                system=system_message,
                messages=[{"role": "user", "content": context}],
            )

            return message.content[0].text

        except Exception as e:
            return f"❌ Claude analysis failed: {str(e)}"

    def _post_review_comment(self, pr_number: int, review_content: str):
        """Post PR review comment"""
        try:
            review_data = {
                "body": f"## 🤖 Claude Code PR Review\n\n{review_content}\n\n---\n*Automated review by Claude Code*",
                "event": "COMMENT",
            }

            self._github_api_request("POST", f"pulls/{pr_number}/reviews", review_data)
            print(f"✅ Posted Claude review to PR #{pr_number}")

        except Exception as e:
            print(f"❌ Failed to post review: {e}")

    def review_pr(self, pr_number: int, base_sha: str, head_sha: str):
        """Main PR review function"""
        try:
            print(f"🔍 Reviewing PR #{pr_number}")

            # Get PR data
            pr_data = self._github_api_request("GET", f"pulls/{pr_number}")

            # Get diff and changed files
            diff_content = self._get_pr_diff(base_sha, head_sha)
            changed_files = self._get_changed_files(pr_number)

            print(f"📁 Analyzing {len(changed_files)} changed files")

            # Analyze with Claude
            review_content = self._analyze_with_claude(
                pr_data, diff_content, changed_files
            )

            # Post review
            self._post_review_comment(pr_number, review_content)

            print("✅ PR review completed")

        except Exception as e:
            print(f"❌ PR review failed: {e}")
            sys.exit(1)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Claude Code PR Reviewer")
    parser.add_argument("--pr-number", type=int, required=True, help="PR number")
    parser.add_argument("--repository", required=True, help="Repository name")
    parser.add_argument("--base-sha", required=True, help="Base commit SHA")
    parser.add_argument("--head-sha", required=True, help="Head commit SHA")

    args = parser.parse_args()

    try:
        print("🚀 Claude Code PR Reviewer starting...")
        print(f"📁 Repository: {args.repository}")
        print(f"🔢 PR: #{args.pr_number}")

        reviewer = ClaudePRReviewer()
        reviewer.review_pr(args.pr_number, args.base_sha, args.head_sha)

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
