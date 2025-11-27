from fastapi import FastAPI, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
import shutil, os
from backend.chains.resume_analyzer import analyze_resume
from backend.chains.job_match_agent import get_best_job_matches

app = FastAPI(title="CareerPath – Resume Analyzer API")

# Allow Streamlit frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev: you can later limit to specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "🚀 CareerPath API is running. Visit /docs for testing."}


@app.post("/analyze")
async def analyze_resume_endpoint(file: UploadFile, target_role: str = Form(...)):
    """Analyze the resume and compute matching insights."""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_resume(temp_path, target_role)
    os.remove(temp_path)
    return result


@app.post("/jobmatch")
async def job_match_endpoint(payload: dict = Body(...)):
    """Return best-matching jobs for a target role with filters."""
    role = payload.get("target_role")
    country = payload.get("country", "us")
    remote = payload.get("remote", False)
    date_posted = payload.get("date_posted", "all")
    num_pages = payload.get("num_pages", 1)

    results = get_best_job_matches(
        role, country=country, remote=remote, date_posted=date_posted, pages=num_pages
    )
    return {"target_role": role, "matches": results}
