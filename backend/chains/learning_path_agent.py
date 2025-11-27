import json
import re
import google.generativeai as genai
from backend.config import GOOGLE_API_KEY
from backend.utils.cache_manager import get_cached_learning, set_cached_learning

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# -----------------------------
# GEMINI HELPER FUNCTION
# -----------------------------
def _generate_with_gemini(prompt_text: str) -> str:
    """Safely generate content from Gemini model."""
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt_text)
        if hasattr(response, "text"):
            return response.text
        return str(response)
    except Exception as e:
        print(f"[gemini] learning path generation error: {e}")
        return ""


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def generate_learning_path(missing_skills: list[str]) -> dict:
    """
    Generates a structured JSON roadmap for each missing skill using Gemini.
    Includes course, video, project, and certification (with links).
    Uses caching to avoid repeated Gemini calls.
    """

    if not missing_skills:
        return {}

    final_output = {}

    for skill in missing_skills:
        # 1️⃣ Check cache first
        cached = get_cached_learning(skill)
        if cached:
            print(f"[cache] Using cached learning path for: {skill}")
            final_output[skill] = cached
            continue

        # 2️⃣ Generate new roadmap with Gemini
        prompt = f"""
You are a helpful AI career mentor.
Generate a structured JSON roadmap for the skill "{skill}" with the following format:

{{
  "course": {{
    "name": "Course title (preferably free)",
    "link": "Direct course URL"
  }},
  "video": {{
    "title": "YouTube tutorial name",
    "link": "YouTube URL"
  }},
  "project": {{
    "idea": "Short project idea",
    "link": "GitHub repo or article link"
  }},
  "certification": {{
    "name": "Certification name",
    "link": "Official certification URL"
  }}
}}

Rules:
- Return ONLY valid JSON (no markdown, text, or commentary).
- Prefer Coursera, YouTube, Udemy, GitHub, and official certification sites.
- Keep names concise and realistic.
"""

        output = _generate_with_gemini(prompt)
        try:
            # Extract and parse valid JSON
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            skill_data = json.loads(json_match.group(0)) if json_match else {}
            if skill_data:
                final_output[skill] = skill_data
                set_cached_learning(skill, skill_data)  # Cache this result
            else:
                print(f"[gemini] No structured data found for: {skill}")
        except Exception as e:
            print(f"[learning path parse error] for {skill}: {e}")

    return final_output
