"""
Resume Scoring Service
- Parses resume text
- Fetches trending skills from Adzuna API
- Computes Market Skill Match (M), Resume Score (R)

Formula:
  M = Trending Skills in Resume / Total Trending Skills
  R = 0.4*M + 0.3*E + 0.3*P
"""
import re
import requests
from config import settings


# ── Trending Skills Fetcher ──────────────────────────────────────────────────

def fetch_trending_skills(job_title: str = "software engineer", country: str = "in") -> list:
    """
    Fetch trending required skills from Adzuna job listings API.
    Falls back to a hardcoded list if API fails.
    """
    try:
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_API_KEY,
            "what": job_title,
            "results_per_page": 20,
            "content-type": "application/json"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract keywords from job descriptions
        all_text = " ".join(
            job.get("description", "") for job in data.get("results", [])
        ).lower()

        return extract_skills_from_text(all_text)

    except Exception:
        # Fallback trending skills for CS/tech roles
        return [
            "python", "machine learning", "deep learning", "fastapi", "django",
            "react", "docker", "kubernetes", "aws", "sql", "postgresql",
            "git", "tensorflow", "pytorch", "nlp", "computer vision",
            "data structures", "algorithms", "system design", "rest api",
            "javascript", "typescript", "ci/cd", "linux", "mongodb"
        ]


def extract_skills_from_text(text: str) -> list:
    """Extract skill keywords from raw text."""
    known_skills = [
        "python", "java", "c++", "javascript", "typescript", "sql", "nosql",
        "react", "angular", "vue", "node", "fastapi", "flask", "django",
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "docker", "kubernetes", "aws", "gcp", "azure", "git", "linux",
        "postgresql", "mongodb", "redis", "elasticsearch",
        "data structures", "algorithms", "system design", "rest api",
        "microservices", "ci/cd", "agile", "xgboost", "llm", "transformers"
    ]
    text_lower = text.lower()
    return [skill for skill in known_skills if skill in text_lower]


# ── Resume Parser ────────────────────────────────────────────────────────────

def parse_resume_skills(resume_text: str) -> list:
    """Extract skills mentioned in the candidate's resume."""
    return extract_skills_from_text(resume_text)


def estimate_experience_score(resume_text: str) -> float:
    """
    Estimate normalized experience score (E) from resume text.
    Based on number of years, internships, and job mentions.
    Returns 0.0 to 1.0
    """
    text_lower = resume_text.lower()
    score = 0.0

    # Years of experience mentioned
    year_matches = re.findall(r'(\d+)\s*(?:\+)?\s*year', text_lower)
    if year_matches:
        max_years = max(int(y) for y in year_matches)
        score += min(1.0, max_years / 5)  # 5 years = full score
    elif "intern" in text_lower or "trainee" in text_lower:
        score += 0.2
    else:
        score += 0.1

    # Has internships
    if "internship" in text_lower or "intern" in text_lower:
        score = min(1.0, score + 0.2)

    # Has work experience / job titles
    if any(w in text_lower for w in ["engineer", "developer", "analyst", "scientist"]):
        score = min(1.0, score + 0.1)

    return round(score, 2)


def estimate_project_score(resume_text: str) -> float:
    """
    Estimate project complexity score (P) from resume text.
    Returns 0.0 to 1.0
    """
    text_lower = resume_text.lower()
    score = 0.0

    # Count project-related keywords
    project_keywords = ["project", "built", "developed", "implemented", "deployed",
                        "designed", "created", "published", "github", "open source"]
    matches = sum(1 for kw in project_keywords if kw in text_lower)
    score += min(0.5, matches * 0.08)

    # Complexity indicators
    complexity_terms = ["api", "database", "cloud", "ml", "ai", "deep learning",
                        "distributed", "microservice", "production", "deployed"]
    complex_matches = sum(1 for t in complexity_terms if t in text_lower)
    score += min(0.5, complex_matches * 0.06)

    return round(min(1.0, score), 2)


# ── Main Resume Scoring ──────────────────────────────────────────────────────

def score_resume(resume_text: str, job_title: str = "software engineer") -> dict:
    """
    Full resume scoring pipeline.
    Returns M, E, P, R scores + matched/missing skills.
    """
    # 1. Fetch trending skills from market
    trending_skills = fetch_trending_skills(job_title)

    # 2. Parse resume skills
    candidate_skills = parse_resume_skills(resume_text)

    # 3. Market Skill Match: M = matching skills / total trending
    matched = [s for s in trending_skills if s in candidate_skills]
    missing = [s for s in trending_skills if s not in candidate_skills]

    M = len(matched) / len(trending_skills) if trending_skills else 0.0

    # 4. Experience and Project scores
    E = estimate_experience_score(resume_text)
    P = estimate_project_score(resume_text)

    # 5. Final Resume Score: R = 0.4M + 0.3E + 0.3P
    R = round(0.4 * M + 0.3 * E + 0.3 * P, 4)

    return {
        "market_skill_match": round(M, 4),
        "experience_score": E,
        "project_score": P,
        "resume_score": R,
        "matched_skills": matched[:15],
        "missing_skills": missing[:15],
        "candidate_skills": candidate_skills
    }
