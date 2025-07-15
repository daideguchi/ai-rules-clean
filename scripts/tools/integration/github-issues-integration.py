#!/usr/bin/env python3
"""
GitHub Issues Integration System for Commitment Tracking
Based on INTEGRITY_RECOVERY_PLAN.md requirements
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CommitmentTracker:
    """Tracks AI commitments through GitHub Issues"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.commitments_file = self.repo_path / "runtime" / "commitments.json"
        self.ensure_runtime_dir()

    def ensure_runtime_dir(self):
        """Ensure runtime directory exists"""
        runtime_dir = self.repo_path / "runtime"
        runtime_dir.mkdir(exist_ok=True)

        if not self.commitments_file.exists():
            self.commitments_file.write_text(
                json.dumps(
                    {
                        "commitments": [],
                        "metadata": {
                            "created": datetime.now().isoformat(),
                            "version": "1.0.0",
                        },
                    },
                    indent=2,
                )
            )

    def create_commitment(
        self,
        description: str,
        estimated_time: str,
        requirements: List[str],
        completion_criteria: str,
    ) -> str:
        """Create a new commitment and GitHub issue"""

        # Generate unique commitment ID
        commitment_id = hashlib.md5(
            f"{description}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]

        # Create GitHub issue
        issue_body = f"""
## 🎯 AI Commitment Tracking

**Commitment ID**: {commitment_id}
**Estimated Time**: {estimated_time}
**Created**: {datetime.now().isoformat()}

### Requirements
{chr(10).join(f"- {req}" for req in requirements)}

### Completion Criteria
{completion_criteria}

### Status
- [ ] Requirements analyzed
- [ ] Implementation started
- [ ] Testing completed
- [ ] Documentation updated
- [ ] Final verification

---
*This issue is automatically managed by the Integrity Recovery System*
"""

        # Create GitHub issue using gh CLI
        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "create",
                    "--title",
                    f"[COMMITMENT] {description}",
                    "--body",
                    issue_body,
                    "--label",
                    "commitment,ai-task",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode != 0:
                print(f"❌ Failed to create GitHub issue: {result.stderr}")
                return None

            # Extract issue number from output
            issue_url = result.stdout.strip()
            issue_number = issue_url.split("/")[-1]

        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub CLI error: {e}")
            return None

        # Store commitment locally
        commitment = {
            "id": commitment_id,
            "description": description,
            "estimated_time": estimated_time,
            "requirements": requirements,
            "completion_criteria": completion_criteria,
            "github_issue": issue_number,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "progress": [],
        }

        # Load existing commitments
        with open(self.commitments_file) as f:
            data = json.load(f)

        data["commitments"].append(commitment)

        # Save updated commitments
        with open(self.commitments_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Commitment created: {commitment_id}")
        print(f"📋 GitHub Issue: {issue_url}")

        return commitment_id

    def update_progress(
        self, commitment_id: str, progress_note: str, status: Optional[str] = None
    ):
        """Update commitment progress"""

        with open(self.commitments_file) as f:
            data = json.load(f)

        for commitment in data["commitments"]:
            if commitment["id"] == commitment_id:
                commitment["progress"].append(
                    {"timestamp": datetime.now().isoformat(), "note": progress_note}
                )

                if status:
                    commitment["status"] = status

                # Update GitHub issue
                issue_number = commitment["github_issue"]
                comment_body = f"**Progress Update**: {progress_note}"
                if status:
                    comment_body += f"\n**Status**: {status}"

                try:
                    subprocess.run(
                        [
                            "gh",
                            "issue",
                            "comment",
                            issue_number,
                            "--body",
                            comment_body,
                        ],
                        cwd=self.repo_path,
                        check=True,
                    )
                    print(f"✅ Progress updated for {commitment_id}")
                except subprocess.CalledProcessError:
                    print(f"⚠️ Failed to update GitHub issue {issue_number}")

                break

        # Save updated commitments
        with open(self.commitments_file, "w") as f:
            json.dump(data, f, indent=2)

    def complete_commitment(self, commitment_id: str, completion_note: str):
        """Mark commitment as completed"""

        with open(self.commitments_file) as f:
            data = json.load(f)

        for commitment in data["commitments"]:
            if commitment["id"] == commitment_id:
                commitment["status"] = "completed"
                commitment["completed_at"] = datetime.now().isoformat()
                commitment["completion_note"] = completion_note

                # Close GitHub issue
                issue_number = commitment["github_issue"]
                close_comment = f"""
## ✅ Commitment Completed

{completion_note}

**Completed**: {datetime.now().isoformat()}

All requirements satisfied and commitment fulfilled.
"""

                try:
                    subprocess.run(
                        [
                            "gh",
                            "issue",
                            "comment",
                            issue_number,
                            "--body",
                            close_comment,
                        ],
                        cwd=self.repo_path,
                        check=True,
                    )

                    subprocess.run(
                        ["gh", "issue", "close", issue_number],
                        cwd=self.repo_path,
                        check=True,
                    )

                    print(f"✅ Commitment {commitment_id} completed and issue closed")
                except subprocess.CalledProcessError:
                    print(f"⚠️ Failed to close GitHub issue {issue_number}")

                break

        # Save updated commitments
        with open(self.commitments_file, "w") as f:
            json.dump(data, f, indent=2)

    def list_active_commitments(self) -> List[Dict]:
        """List all active commitments"""

        with open(self.commitments_file) as f:
            data = json.load(f)

        active = [c for c in data["commitments"] if c["status"] != "completed"]

        if not active:
            print("✅ No active commitments")
            return []

        print(f"📋 Active Commitments ({len(active)}):")
        for commitment in active:
            print(f"  {commitment['id']}: {commitment['description']}")
            print(f"    Status: {commitment['status']}")
            print(f"    GitHub: #{commitment['github_issue']}")
            print()

        return active

    def check_overdue_commitments(self):
        """Check for overdue commitments and create alerts"""

        with open(self.commitments_file) as f:
            data = json.load(f)

        overdue = []
        now = datetime.now()

        for commitment in data["commitments"]:
            if commitment["status"] == "pending":
                created = datetime.fromisoformat(commitment["created_at"])
                hours_elapsed = (now - created).total_seconds() / 3600

                # Alert if no progress for 24 hours
                if hours_elapsed > 24 and not commitment["progress"]:
                    overdue.append(commitment)

        if overdue:
            print(f"🚨 {len(overdue)} overdue commitments detected!")
            for commitment in overdue:
                print(f"  ⏰ {commitment['id']}: {commitment['description']}")

                # Add urgent comment to GitHub issue
                issue_number = commitment["github_issue"]
                alert_comment = f"""
🚨 **OVERDUE COMMITMENT ALERT**

This commitment has been pending for over 24 hours with no progress updates.

**Action Required**:
- Provide immediate progress update
- Or formally abandon/postpone this commitment
- Or break down into smaller tasks

**Commitment ID**: {commitment["id"]}
**Created**: {commitment["created_at"]}
"""

                try:
                    subprocess.run(
                        [
                            "gh",
                            "issue",
                            "comment",
                            issue_number,
                            "--body",
                            alert_comment,
                        ],
                        cwd=self.repo_path,
                        check=True,
                    )

                    # Add urgent label
                    subprocess.run(
                        [
                            "gh",
                            "issue",
                            "edit",
                            issue_number,
                            "--add-label",
                            "urgent,overdue",
                        ],
                        cwd=self.repo_path,
                        check=True,
                    )

                except subprocess.CalledProcessError:
                    print(f"⚠️ Failed to update overdue issue {issue_number}")

        return overdue


def main():
    """CLI interface for commitment tracking"""

    if len(sys.argv) < 2:
        print("Usage: python github-issues-integration.py <command> [args...]")
        print("Commands: create, update, complete, list, check-overdue")
        return

    tracker = CommitmentTracker()
    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 6:
            print(
                "Usage: create <description> <time> <requirements> <completion_criteria>"
            )
            return

        description = sys.argv[2]
        time = sys.argv[3]
        requirements = sys.argv[4].split(",")
        criteria = sys.argv[5]

        tracker.create_commitment(description, time, requirements, criteria)

    elif command == "update":
        if len(sys.argv) < 4:
            print("Usage: update <commitment_id> <progress_note> [status]")
            return

        commitment_id = sys.argv[2]
        progress_note = sys.argv[3]
        status = sys.argv[4] if len(sys.argv) > 4 else None

        tracker.update_progress(commitment_id, progress_note, status)

    elif command == "complete":
        if len(sys.argv) < 4:
            print("Usage: complete <commitment_id> <completion_note>")
            return

        commitment_id = sys.argv[2]
        completion_note = sys.argv[3]

        tracker.complete_commitment(commitment_id, completion_note)

    elif command == "list":
        tracker.list_active_commitments()

    elif command == "check-overdue":
        tracker.check_overdue_commitments()

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
