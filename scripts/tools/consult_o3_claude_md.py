#!/usr/bin/env python3
"""
Consult o3 about CLAUDE.md best practices
"""

import os
import sys
from pathlib import Path

from openai import OpenAI

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def consult_o3_about_claude_md():
    """Ask o3 for CLAUDE.md optimization recommendations"""

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = """As o3 AI system, please analyze and provide recommendations for optimizing CLAUDE.md documentation structure.

Based on 2025 best practices for Claude Code memory system, please advise on:

1. **Optimal Structure**: What should be the ideal section ordering and hierarchy?
2. **Conciseness vs Completeness**: How to balance being concise (to save tokens) while maintaining completeness?
3. **Import Strategy**: When should we use @imports vs inline content?
4. **Critical vs Optional Content**: What absolutely must be in CLAUDE.md vs what can be moved to docs/?
5. **Performance Optimization**: How to structure for fastest session initialization?
6. **Team Collaboration**: Best practices for shared project memory?

Current CLAUDE.md has these sections:
- CRITICAL PROCEDURES (session init, emergency response)
- SYSTEM REQUIREMENTS (display, orchestration, language rules)
- CORE SYSTEMS ARCHITECTURE (AI safety, memory, execution)
- OPERATIONAL PROCEDURES (standard ops, testing, monitoring)
- REFERENCE INFORMATION (project structure, rules)
- SYSTEM STATUS & METRICS
- ABSOLUTE PROHIBITIONS
- APPENDICES

Please provide specific, actionable recommendations for improvement."""

    try:
        response = client.chat.completions.create(
            model="o1-preview",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4000,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error consulting o3: {str(e)}"


if __name__ == "__main__":
    print("🤖 Consulting o3 about CLAUDE.md best practices...\n")
    recommendations = consult_o3_about_claude_md()
    print(recommendations)

    # Save recommendations
    output_path = (
        project_root / "docs" / "_analysis" / "o3_claude_md_recommendations.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write("# o3 Recommendations for CLAUDE.md Optimization\n\n")
        f.write(recommendations)

    print(f"\n✅ Recommendations saved to: {output_path}")
