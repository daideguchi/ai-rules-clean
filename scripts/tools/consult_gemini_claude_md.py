#!/usr/bin/env python3
"""
Consult Gemini about CLAUDE.md best practices via Google Generative AI
"""

import os
import sys
from pathlib import Path

import google.generativeai as genai

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_latest_gemini_model():
    """Dynamically get the latest available Gemini model from API"""
    try:
        # List all available models
        models = genai.list_models()

        # Filter for Gemini models that support generateContent
        gemini_models = []
        for model in models:
            if (
                model.name.startswith("models/gemini-")
                and "generateContent" in model.supported_generation_methods
            ):
                gemini_models.append(model.name.replace("models/", ""))

        # Sort by version (prioritize 2.5 > 2.0 > 1.5, then pro > flash for quality)
        def model_priority(model_name):
            version_score = 0
            if "gemini-2.5" in model_name:
                version_score = 250
            elif "gemini-2.0" in model_name:
                version_score = 200
            elif "gemini-1.5" in model_name:
                version_score = 150

            # Prefer flash for free tier availability, then pro for quality
            if "flash" in model_name and "preview" not in model_name:
                version_score += 20  # Highest priority for stable flash (free tier)
            elif "pro" in model_name and "preview" not in model_name:
                version_score += 15  # Pro but not preview
            elif "flash" in model_name:
                version_score += 10  # Flash preview
            elif "pro" in model_name:
                version_score += 5  # Pro preview (paid tier)

            return version_score

        # Get the highest priority model
        if gemini_models:
            latest_model = max(gemini_models, key=model_priority)
            print(f"🤖 Dynamically selected latest model: {latest_model}")
            return latest_model
        else:
            print("⚠️ No Gemini models found, falling back to gemini-1.5-flash")
            return "gemini-1.5-flash"

    except Exception as e:
        print(f"⚠️ Error fetching models: {e}, falling back to gemini-1.5-flash")
        return "gemini-1.5-flash"


def consult_gemini_about_claude_md():
    """Ask Gemini for CLAUDE.md optimization recommendations"""

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # Dynamically get latest model
    latest_model = get_latest_gemini_model()
    model = genai.GenerativeModel(latest_model)

    prompt = """As Gemini 2.5 Pro AI system, please analyze and provide recommendations for optimizing CLAUDE.md documentation structure based on 2025 best practices from Japanese research articles.

Key research findings to incorporate:
- CLAUDE.md should be under 100 lines (current: 648 lines)
- Use @import syntax for modular file splitting (max 5 hops)
- Structure as "operational device" not "specification document"
- Self-improvement loops enabling Claude to learn from operations
- Emphasis on IMPORTANT/YOU MUST for critical compliance
- Language separation: claude_lang/en.md, claude_lang/ja.md
- Knowledge management with update rules and guard rails
- "Bootloader" concept: minimal core + essential imports

Current critical issues:
1. Monolithic 648-line file violates 100-line best practice
2. Mixed critical/reference content reduces session efficiency
3. Japanese/English mixing needs language pack separation
4. Missing self-learning integration structure
5. Overuse of emphasis reduces effectiveness

Provide specific, actionable recommendations for:

1. **Core Bootloader Design**: What 20-30 lines should remain in main CLAUDE.md for session initialization?
2. **Import Architecture**: 4-layer structure (Core→Essential→Specific→Reference) with specific file names
3. **Language Pack Strategy**: Optimal separation of multilingual instructions
4. **Emphasis Optimization**: Strategic placement of IMPORTANT/YOU MUST for maximum compliance
5. **Self-Learning Integration**: Continuous improvement mechanisms with learning protocols
6. **Implementation Roadmap**: Step-by-step migration plan from current 648-line structure

Focus on Japanese best practices: "operational device", knowledge management, and self-improvement loops."""

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error consulting Gemini: {str(e)}"


if __name__ == "__main__":
    print("💎 Consulting Gemini about CLAUDE.md best practices...\n")
    recommendations = consult_gemini_about_claude_md()
    print(recommendations)

    # Save recommendations
    output_path = (
        project_root / "docs" / "_analysis" / "gemini_claude_md_recommendations.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write("# Gemini Recommendations for CLAUDE.md Optimization\n\n")
        f.write(recommendations)

    print(f"\n✅ Recommendations saved to: {output_path}")
