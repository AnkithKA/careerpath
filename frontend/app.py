import streamlit as st
import requests

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(page_title="CareerPath – AI Career Navigator", page_icon="💼", layout="wide")

BACKEND_ANALYZE_URL = "http://127.0.0.1:8000/analyze"
BACKEND_JOBMATCH_URL = "http://127.0.0.1:8000/jobmatch"

st.markdown(
    """
    <h1 style='text-align:center; color:#E2E8F0;'>💼 CareerPath – AI Career Navigator</h1>
    <p style='text-align:center; color:#9CA3AF; font-size:16px;'>
    Upload your resume, specify your dream role, and let AI analyze, guide, and match you to real jobs.
    </p>
    """,
    unsafe_allow_html=True,
)

# ==============================
# SESSION STATE SETUP
# ==============================
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "result" not in st.session_state:
    st.session_state.result = {}
if "job_results" not in st.session_state:
    st.session_state.job_results = []

# ==============================
# SIDEBAR — INPUTS
# ==============================
with st.sidebar:
    st.header("⚙️ Input Details")
    uploaded_file = st.file_uploader("📄 Upload Resume (PDF only)", type=["pdf"])
    target_role = st.text_input("🎯 Target Role", placeholder="e.g., Data Scientist")

    analyze_btn = st.button("🚀 Analyze Resume", use_container_width=True)

# ==============================
# ANALYSIS LOGIC
# ==============================
if analyze_btn:
    if not uploaded_file or not target_role:
        st.warning("Please upload a resume and specify your target role.")
    else:
        with st.spinner("Analyzing your resume with AI... 🔍"):
            try:
                files = {"file": uploaded_file}
                data = {"target_role": target_role}
                response = requests.post(BACKEND_ANALYZE_URL, files=files, data=data)

                if response.status_code == 200:
                    result = response.json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.analyzed = True
                        st.session_state.result = result
                        st.success("✅ Resume analyzed successfully!")
                else:
                    st.error(f"❌ Server error: {response.status_code}")
            except Exception as e:
                st.error(f"💥 Backend connection failed: {e}")

# ============================================
# DISPLAY RESULTS IF ANALYZED
# ============================================
if st.session_state.analyzed:
    result = st.session_state.result
    tabs = st.tabs(["📊 Summary", "🧠 Extracted Info", "🎓 Learning Roadmap", "💼 Job Matches"])

    # ------------------ TAB 1 ------------------
    with tabs[0]:
        st.markdown("### 📋 Overview Summary")
        st.markdown(
            f"<div style='background-color:#1E293B; padding:15px; border-radius:10px; color:#E2E8F0;'>"
            f"<b>🎯 Target Role:</b> {target_role}<br>"
            f"<b>📊 Match Score:</b> {result.get('match_score', 0):.2f}%<br>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("### 🧾 Job Description (Generated)")
        st.info(result.get("job_description", "N/A"))

        st.markdown("### ❌ Missing Skills")
        if result.get("missing_skills"):
            st.markdown(
                " ".join(
                    [f"<span style='background-color:#7F1D1D; color:#FEE2E2; padding:4px 8px; border-radius:10px; margin:3px; display:inline-block;'>{m}</span>"
                     for m in result["missing_skills"]]
                ),
                unsafe_allow_html=True,
            )
        else:
            st.success("No missing skills detected — you're aligned perfectly! 🎯")

    # ------------------ TAB 2 ------------------
    with tabs[1]:
        st.markdown("### 🧠 AI-Extracted Resume Data")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧩 Skills")
            if result.get("skills"):
                st.markdown(
                    " ".join(
                        [f"<span style='background-color:#1E293B; color:#E2E8F0; padding:5px 8px; border-radius:8px; margin:3px; display:inline-block;'>{s}</span>"
                         for s in result["skills"]]
                    ),
                    unsafe_allow_html=True,
                )

            st.subheader("⚙️ Tools & Technologies")
            if result.get("tools"):
                st.markdown(
                    " ".join(
                        [f"<span style='background-color:#334155; color:#E2E8F0; padding:5px 8px; border-radius:8px; margin:3px; display:inline-block;'>{t}</span>"
                         for t in result["tools"]]
                    ),
                    unsafe_allow_html=True,
                )

        with col2:
            st.subheader("💼 Experience Summary")
            if result.get("experience"):
                with st.container():
                    st.markdown(
                        "<div style='background-color:#0f172a; padding:15px; border-radius:10px;'>"
                        + "<br>".join([f"• {exp}" for exp in result["experience"]])
                        + "</div>",
                        unsafe_allow_html=True,
                    )

    # ------------------ TAB 3 ------------------
    with tabs[2]:
        st.markdown("### 🎓 Personalized Upskilling Roadmap")
        roadmap = result.get("learning_roadmap", {})
        if roadmap:
            for skill, details in roadmap.items():
                with st.expander(f"📘 {skill}", expanded=False):
                    for k, v in details.items():
                        if isinstance(v, dict) and "name" in v and "link" in v:
                            st.markdown(f"- **{k.title()}**: [{v['name']}]({v['link']})")
        else:
            st.info("No roadmap generated — looks like your skills already match well!")

    # ------------------ TAB 4 ------------------
    with tabs[3]:
        st.markdown("### 💼 Matched Job Opportunities")
        st.markdown("#### 🔍 Refine Job Search")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            country = st.selectbox("🌍 Country", ["us", "in", "ca", "uk", "de", "au"], index=1, key="country_filter")
        with col2:
            remote_only = st.checkbox("💻 Remote Only", value=False, key="remote_filter")
        with col3:
            date_posted = st.selectbox("🗓️ Date Posted", ["today", "3days", "week", "month", "all"], index=4, key="date_filter")
        with col4:
            num_pages = st.slider("📄 Results Pages", 1, 5, 1, key="pages_filter")

        fetch_jobs = st.button("🔎 Fetch Matching Jobs", use_container_width=True, key="fetch_button")

        if fetch_jobs:
            try:
                with st.spinner("Fetching latest job openings..."):
                    job_params = {
                        "target_role": target_role.strip(),
                        "country": country,
                        "remote": remote_only,
                        "date_posted": date_posted,
                        "num_pages": num_pages
                    }

                    job_response = requests.post(BACKEND_JOBMATCH_URL, json=job_params, timeout=60)
                    if job_response.status_code == 200:
                        job_data = job_response.json()
                        st.session_state.job_results = job_data.get("matches", [])
                    else:
                        st.warning("⚠️ Could not fetch job matches.")
            except Exception as e:
                st.error(f"💥 Error fetching job matches: {e}")

        if st.session_state.job_results:
            for job in st.session_state.job_results:
                st.markdown(
                    f"""
                    <div style="background-color:#1e293b; padding:15px; border-radius:10px; margin-bottom:10px;">
                        <h4 style="color:#E2E8F0;">{job.get('title', 'Untitled Role')} — <span style="color:#94A3B8;">{job.get('company', 'Unknown')}</span></h4>
                        <p style="color:#CBD5E1;">{job.get('description', '')[:400]}...</p>
                        <p style="color:#A3E635;">Match Score: {round(job.get('score', 0)*100, 2)}%</p>
                        {'<a href="'+job.get('link', '#')+'" target="_blank" style="color:#60A5FA;">🔗 Apply Here</a>' if job.get('link') else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

else:
    st.info("📎 Upload your resume and enter a target role to begin analysis.")
