# 💼 CareerPath – AI Career Navigator

> An intelligent resume analysis and job matching platform powered by LLMs and semantic search. Upload your resume, define your target role, and discover the perfect job opportunities with AI-generated learning roadmaps.

---

## 🎯 What is CareerPath?

**CareerPath** is an end-to-end AI-powered career guidance system that:

- 📄 **Analyzes Resumes** – Extracts skills, experience, and qualifications using PDF parsing and embeddings
- 🎓 **Generates Learning Paths** – Creates personalized roadmaps for missing skills with courses, projects, and certifications
- 💼 **Matches Jobs** – Fetches real-time job listings and ranks them by semantic similarity to your profile
- 🧠 **Uses Advanced AI** – Leverages Google's Gemini LLM and semantic embeddings for intelligent matching

---

## ✨ Key Features

### 📊 **Resume Analysis**
- Extract and analyze skills, experience, and education from PDF resumes
- Calculate skill gap analysis between your resume and target role
- Generate a synthetic job description for your target role
- Compute match score based on semantic similarity

### 🚀 **Job Matching**
- Fetch real jobs from JSearch API with filters (location, remote, date posted)
- Rank jobs using semantic similarity embeddings
- Display top matching opportunities with links and descriptions
- Support for multiple countries and job filters

### 🎓 **Learning Roadmaps**
- Generate AI-powered learning paths for each missing skill
- Include courses, YouTube videos, hands-on projects, and certifications
- Cached roadmaps for fast retrieval
- Direct links to resources

### 💾 **Smart Caching**
- Cache job descriptions, learning paths, and job listings
- Avoid redundant API calls and LLM generations
- Fast retrieval for repeated queries

---

## 🏗️ Architecture

```
careerpath/
├── frontend/
│   └── app.py                    # Streamlit UI
├── backend/
│   ├── main.py                   # FastAPI server
│   ├── config.py                 # Configuration & env variables
│   ├── chains/
│   │   ├── resume_analyzer.py    # Resume analysis logic
│   │   ├── job_match_agent.py    # Job fetching & matching
│   │   └── learning_path_agent.py# Learning roadmap generation
│   ├── utils/
│   │   ├── parsers.py            # PDF extraction
│   │   ├── embeddings.py         # Semantic embedding models
│   │   ├── cache_manager.py      # Caching logic
│   │   └── pinecone_manager.py   # Vector DB integration
│   └── data/
│       ├── job_cache.json        # Cached job listings
│       └── jd_cache.json         # Cached job descriptions
└── README.md
```

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit** – Interactive web interface
- **Requests** – HTTP client for backend communication

### Backend
- **FastAPI** – Modern Python web framework
- **Google Generative AI (Gemini 2.5)** – LLM for analysis and insights
- **Sentence Transformers** – Semantic embeddings
- **Pinecone** – Vector database for semantic search
- **PyPDF** – PDF parsing and text extraction
- **Scikit-learn** – Cosine similarity for job matching
- **LangChain** – Chain orchestration

### APIs & Services
- **JSearch API** – Real-time job listings
- **Google Generative AI** – LLM capabilities
- **Pinecone** – Vector embeddings storage

---

## 📋 Prerequisites

- **Python 3.9+**
- **Streamlit** (frontend)
- **FastAPI & Uvicorn** (backend)
- Environment variables configured (`.env` file):
  - `GOOGLE_API_KEY` – Google Generative AI API key
  - `PINECONE_API_KEY` – Pinecone API key
  - `PINECONE_ENV` – Pinecone environment (default: `us-east1-gcp`)
  - `PINECONE_INDEX_NAME` – Pinecone index name (default: `careerpath-job-index`)
  - `RAPIDAPI_KEY` – RapidAPI key for JSearch

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/careerpath.git
cd careerpath
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=us-east1-gcp
PINECONE_INDEX_NAME=careerpath-job-index
RAPIDAPI_KEY=your_rapidapi_key_here
```

### 4. Run the Backend (FastAPI)
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
The API will be available at `http://127.0.0.1:8000`

### 5. Run the Frontend (Streamlit)
In a new terminal:
```bash
cd frontend
streamlit run app.py
```
The UI will open at `http://localhost:8501`

---

## 📖 How It Works

### 1️⃣ **Upload Resume & Specify Target Role**
- User uploads a PDF resume
- Specifies the desired career role

### 2️⃣ **Resume Analysis**
- Backend extracts text from PDF
- Generates embeddings for resume content
- Generates synthetic job description for target role
- Computes skill gaps between resume and target role

### 3️⃣ **Match Scoring**
- Calculates semantic similarity between resume and target role
- Identifies missing skills
- Returns match score and insights

### 4️⃣ **Learning Path Generation**
- For each missing skill, Gemini generates:
  - Recommended online courses
  - YouTube videos
  - Hands-on projects
  - Certification paths
- Results are cached for future reference

### 5️⃣ **Job Matching**
- Fetches real jobs from JSearch API
- Filters by location, remote status, date posted
- Ranks jobs using semantic similarity
- Returns top matching opportunities

---

## 📊 Sample Output

### Resume Analysis Result
```json
{
  "match_score": 72.5,
  "job_description": "Data Scientist with 5+ years of experience in ML and Python...",
  "missing_skills": ["Deep Learning", "Computer Vision", "MLOps"],
  "learning_path": {
    "Deep Learning": {
      "courses": ["..."],
      "videos": ["..."],
      "projects": ["..."],
      "certifications": ["..."]
    }
  }
}
```

### Job Matching Result
```json
{
  "target_role": "Data Scientist",
  "matches": [
    {
      "job_title": "Senior Data Scientist",
      "company": "Tech Corp",
      "location": "Remote",
      "match_score": 89.3,
      "link": "https://..."
    }
  ]
}
```

---

## 🔌 API Endpoints

### `POST /analyze`
Analyze a resume and generate insights.
- **Request**: Multipart form with `file` (PDF) and `target_role` (string)
- **Response**: Analysis with match score, missing skills, and learning paths

### `POST /jobmatch`
Find best-matching jobs for a target role.
- **Request**: JSON with `target_role`, `country`, `remote`, `date_posted`, `num_pages`
- **Response**: List of matching jobs with scores

### `GET /`
Health check endpoint.

---

## 🧠 Core Algorithms

### Semantic Matching
- Uses **Sentence Transformers** to generate embeddings
- Computes **cosine similarity** between resume and job descriptions
- Ranks jobs based on similarity scores

### Caching Strategy
- **Job Descriptions**: Cached locally in `jd_cache.json`
- **Learning Paths**: Cached in `data_cache.json`
- **Job Listings**: Cached in `job_cache.json`
- Reduces API calls and accelerates response times

### LLM Integration
- **Gemini 2.5 Flash**: Generates job descriptions, learning paths, and insights
- Prompt engineering for consistent, structured outputs
- Error handling for API failures

---

## 🎨 Frontend Features

### 📋 **Summary Tab**
- Overview of resume analysis
- Match score visualization
- Missing skills display
- Generated job description

### 🧠 **Extracted Info Tab**
- Parsed resume skills, experience, education
- Structured resume information

### 🎓 **Learning Roadmap Tab**
- Interactive learning paths for each missing skill
- Expandable course/project/certification sections
- Direct links to resources

### 💼 **Job Matches Tab**
- Real-time job listings
- Rank by match score
- Filters for location, remote status, date posted
- Direct links to job postings

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License – see the LICENSE file for details.

---

## 🙋 Support & Contact

- **Issues**: Open an issue on GitHub for bug reports or feature requests
- **Email**: your.email@example.com

---

## 🌟 Acknowledgments

- Google Generative AI (Gemini) for powerful LLM capabilities
- Pinecone for vector database infrastructure
- JSearch API for real-time job data
- Streamlit and FastAPI communities for excellent frameworks

---


*Learn with purpose. Apply with confidence. Land the role you deserve. — CareerPath*
