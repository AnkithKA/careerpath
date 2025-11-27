import json
import re
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
from backend.utils.parsers import extract_text_from_pdf
from backend.utils.embeddings import get_embedding_model
from backend.chains.learning_path_agent import generate_learning_path
from backend.utils.cache_manager import get_cached_jd, set_cached_jd
from backend.config import GOOGLE_API_KEY

# ==============================
# CONFIGURATION
# ==============================
genai.configure(api_key=GOOGLE_API_KEY)
embedding_model = get_embedding_model()


# ==============================
# GEMINI HELPER
# ==============================
def _generate_with_gemini(prompt_text: str) -> str:
    """Generate text using Gemini safely."""
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt_text)

        if hasattr(response, "text"):
            return response.text
        elif hasattr(response, "candidates"):
            return "".join(
                part.text
                for c in response.candidates
                for part in c.content.parts
                if hasattr(part, "text")
            )
        else:
            return str(response)
    except Exception as e:
        print(f"[gemini] generation error: {e}")
        return ""


# ==============================
# JD GENERATOR (Cached + Dynamic)
# ==============================
def generate_job_description(target_role: str) -> str:
    """Generate or retrieve cached JD for the given role (using cache_manager)."""
    cached_jd = get_cached_jd(target_role)
    if cached_jd:
        print(f"[cache] Using cached JD for '{target_role}'")
        return cached_jd

    print(f"[gemini] Generating new JD for '{target_role}'...")
    jd_prompt = (
        f"You are an HR expert generating a concise, skills-only summary for a {target_role}.\n"
        f"Write a 2–3 line technical JD focused **only on key domain & technical skills**.\n"
        f"No company info or soft skills.\n\n"
        f"Example:\n"
        f"For 'Data Scientist': 'Looking for expertise in Python, SQL, Machine Learning, Deep Learning, "
        f"Data Visualization, TensorFlow, and cloud tools like AWS or GCP.'\n\n"
        f"Now generate for '{target_role}':"
    )

    jd_text = _generate_with_gemini(jd_prompt).strip()
    if not jd_text:
        jd_text = f"Seeking a {target_role} skilled in Python, SQL, problem-solving, and modern tools."

    set_cached_jd(target_role, jd_text)
    print(f"[cache] JD for '{target_role}' cached successfully ✅")

    return jd_text


# ==============================
# GEMINI-BASED MISSING SKILLS DETECTION
# ==============================
def _find_missing_skills_with_gemini(resume_skills, jd_text):
    """Use Gemini to reason about missing skills semantically."""
    try:
        skills_str = ", ".join(resume_skills) if resume_skills else "None"
        prompt = (
            "You are a technical recruiter.\n"
            "Compare the candidate's skills with the job description below and identify only the missing "
            "or weakly represented technical skills.\n"
            "Return the result as a valid JSON list like: [\"AWS\", \"Docker\", \"Kubernetes\"] — nothing else.\n\n"
            f"Candidate Skills: {skills_str}\n\n"
            f"Job Description:\n{jd_text}\n"
        )

        response = _generate_with_gemini(prompt)
        json_match = re.search(r"\[.*\]", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        print(f"[gemini missing skills] error: {e}")
    return []


# ==============================
# LOCAL FALLBACK MISSING SKILLS DETECTION
# ==============================
def _find_missing_skills_locally(resume_text, jd_text):
    """Fallback local method using regex for technical keywords."""
    jd_tokens = re.findall(r"\b[A-Za-z\+\#\.\/0-9]+\b", jd_text)
    ignore_terms = {
        "We", "Looking", "Strong", "Ability", "Skills", "Proficiency", "Experience",
        "Excellent", "Capable", "Develop", "Design", "Drive", "Expertise", "Work",
        "Collaborate", "Implement", "Build", "Good", "Familiar", "Knowledge",
        "Understanding", "Engineer", "Role", "Using", "Required", "Preferred", "Job",
        "Seeking", "Position", "Great", "Must", "Should", "Skill"
    }

    jd_skills = [
        token for token in jd_tokens
        if token[0].isupper() and token not in ignore_terms and len(token) > 2
    ]
    jd_skills = list(dict.fromkeys(jd_skills))
    missing_skills = [
        skill for skill in jd_skills
        if skill.lower() not in resume_text.lower()
    ]
    return missing_skills


# ==============================
# MAIN ANALYZER FUNCTION
# ==============================
def analyze_resume(file_path: str, target_role: str):
    """Analyze resume, extract structured data, compute similarity, and generate roadmap."""
    resume_text = extract_text_from_pdf(file_path)
    if not resume_text.strip():
        return {"error": "Failed to read resume text."}

    # STEP 1: Extract structured resume info
    extraction_prompt = (
        "You are a structured resume parser.\n"
        "Analyze the resume and output only valid JSON with this structure:\n"
        "{\n"
        "  \"skills\": [\"Python\", \"Machine Learning\", ...],\n"
        "  \"tools\": [\"TensorFlow\", \"Git\", ...],\n"
        "  \"experience\": [\"Developed ML models\", ...]\n"
        "}\n\n"
        f"Resume:\n{resume_text}"
    )

    raw_output = _generate_with_gemini(extraction_prompt)
    resume_data = {"skills": [], "tools": [], "experience": []}

    try:
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if json_match:
            resume_data = json.loads(json_match.group(0))
    except Exception as e:
        print(f"[json parse] error: {e}")

    # STEP 2: Generate or fetch cached JD
    jd_text = generate_job_description(target_role)

    # STEP 3: Compute similarity score
    all_resume_text = " ".join(resume_data.get("skills", []))
    try:
        resume_vec = embedding_model.encode([all_resume_text])
        jd_vec = embedding_model.encode([jd_text])
        match_score = float(cosine_similarity(resume_vec, jd_vec)[0][0])
    except Exception as e:
        print(f"[embeddings] error: {e}")
        match_score = 0.0

    # STEP 4: Determine missing skills intelligently
    if match_score < 0.8:  # Use Gemini when match score < 80%
        print(f"[gemini] Using AI-based missing skill detection (match={match_score:.2f})")
        missing_skills = _find_missing_skills_with_gemini(resume_data.get("skills", []), jd_text)
    else:
        print(f"[local] Using fast local detection (match={match_score:.2f})")
        missing_skills = _find_missing_skills_locally(all_resume_text, jd_text)

    # STEP 5: Generate learning roadmap using caching
    learning_roadmap = {}
    if missing_skills:
        print(f"[gemini/cache] Generating or reusing learning roadmap for {len(missing_skills)} skills...")
        learning_roadmap = generate_learning_path(missing_skills)

    # Final structured response
    return {
        "skills": resume_data.get("skills", []),
        "tools": resume_data.get("tools", []),
        "experience": resume_data.get("experience", []),
        "job_description": jd_text,
        "match_score": round(match_score * 100, 2),
        "missing_skills": missing_skills,
        "learning_roadmap": learning_roadmap,
    }
