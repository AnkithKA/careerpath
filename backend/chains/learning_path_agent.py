import json
import re
import google.generativeai as genai

from backend.config import GOOGLE_API_KEY
from backend.utils.cache_manager import get_cached_learning, set_cached_learning

# ==============================
# GEMINI CONFIG
# ==============================
genai.configure(api_key=GOOGLE_API_KEY)


# ==============================
# GEMINI HELPER (ROBUST)
# ==============================
def _generate_with_gemini(prompt_text: str) -> str:
    """Safely generate content from Gemini model."""
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt_text)

        if hasattr(response, "text") and response.text:
            return response.text

        if hasattr(response, "candidates"):
            return "".join(
                part.text
                for c in response.candidates
                for part in c.content.parts
                if hasattr(part, "text")
            )

        return ""

    except Exception as e:
        print(f"[gemini] learning path generation error: {e}")
        return ""


# ==============================
# MAIN FUNCTION
# ==============================
def generate_learning_path(missing_skills: list[str]) -> dict:
    """
    Generates a structured JSON roadmap for each missing skill.
    Uses Redis cache to avoid repeated Gemini calls.
    """

    if not missing_skills:
        return {}

    final_output = {}

    for skill in missing_skills:
        # ---------- 0️⃣ BASIC SANITY CHECK ----------
        if not skill or len(skill.strip()) < 2:
            continue

        skill_key = skill.lower().strip()

        # ---------- 1️⃣ CACHE CHECK ----------
        cached = get_cached_learning(skill_key)
        if cached:
            print(f"[redis] Using cached learning path for: {skill}")
            final_output[skill] = cached
            continue

        # ---------- 2️⃣ GEMINI PROMPT (OLD, WORKING VERSION) ----------
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
- Return ONLY valid JSON (no markdown, no explanations).
- Prefer Coursera, YouTube, Udemy, GitHub, and official certification sites.
- Keep names concise and realistic.
"""

        raw_output = _generate_with_gemini(prompt)

        # ---------- 3️⃣ PARSE JSON SAFELY ----------
        try:
            json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
            roadmap = json.loads(json_match.group(0)) if json_match else {}

            if roadmap:
                final_output[skill] = roadmap
                set_cached_learning(skill_key, roadmap)
                print(f"[redis] Cached learning path for: {skill}")
            else:
                print(f"[learning] No structured roadmap for: {skill}")

        except Exception as e:
            print(f"[learning parse error] for {skill}: {e}")

    return final_output
