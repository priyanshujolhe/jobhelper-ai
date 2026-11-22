import re
from app.ml.feature_extraction import compute_tfidf_similarity


def parse_years_of_experience(text: str) -> float:
    """
    Extracts maximum years of experience mentioned in text.
    Handles patterns like '3+ years', '5 years of experience', '2 to 4 years'.
    """
    if not text:
        return 0.0

    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:to\s*(\d+(?:\.\d+)?))?\s*(?:years?|yrs?)(?:\s+of\s+experience)?",
        r"(?:experience|worked for)\s*:\s*(\d+(?:\.\d+)?)\s*years?",
    ]

    max_years = 0.0
    for pat in patterns:
        matches = re.finditer(pat, text, re.IGNORECASE)
        for m in matches:
            groups = m.groups()
            for g in groups:
                if g:
                    try:
                        val = float(g)
                        if val <= 35:  # Avoid parsing years like 2020 as experience
                            if val > max_years:
                                max_years = val
                    except ValueError:
                        pass
    return max_years


def detect_education_level(text: str) -> int:
    """
    Detects education level rank from text:
    4 = PhD / Doctorate
    3 = Master's / MS / M.Tech / MBA
    2 = Bachelor's / BS / B.Tech / BE / B.Sc / BA
    1 = Associate / Diploma
    0 = Unspecified / High School
    """
    if not text:
        return 0

    lower = text.lower()
    if any(k in lower for k in ["ph.d", "phd", "doctorate", "doctoral"]):
        return 4
    if any(k in lower for k in ["master", "m.s.", "m.s", "m.tech", "mba", "msc", "m.sc", "postgraduate"]):
        return 3
    if any(k in lower for k in ["bachelor", "b.s.", "b.s", "b.tech", "b.e.", "b.sc", "undergraduate", "b.a."]):
        return 2
    if any(k in lower for k in ["associate", "diploma", "polytechnic"]):
        return 1
    return 0


def calculate_experience_score(resume_exp_years: float, resume_text: str, job_exp_str: str, job_text: str) -> tuple[float, str]:
    """
    Calculates 0-100 score for experience compatibility.
    """
    req_years = parse_years_of_experience(job_exp_str or "")
    if req_years == 0:
        req_years = parse_years_of_experience(job_text)

    cand_years = resume_exp_years
    if cand_years == 0:
        cand_years = parse_years_of_experience(resume_text)

    # Check for senior / lead keywords in job
    job_lower = (job_exp_str + " " + job_text).lower()
    resume_lower = resume_text.lower()

    is_senior_job = any(k in job_lower for k in ["senior", "sr.", "lead", "principal", "architect"])
    is_junior_job = any(k in job_lower for k in ["junior", "entry level", "intern", "associate developer", "graduate"])

    is_senior_cand = any(k in resume_lower for k in ["senior", "lead", "architect", "manager"])

    if req_years == 0:
        # Default baseline if no explicit year requirement
        if is_senior_job and not is_senior_cand and cand_years < 3:
            return 60.0, "Job prefers senior-level experience; candidate profile appears entry/mid-level."
        elif is_junior_job or cand_years >= 1:
            return 90.0, "Candidate profile aligns well with general experience expectations."
        else:
            return 80.0, "Experience criteria satisfied."

    if cand_years >= req_years:
        score = 100.0
        msg = f"Candidate experience ({cand_years:.1f} yrs) meets or exceeds requirement ({req_years:.1f} yrs)."
    elif cand_years > 0:
        ratio = cand_years / req_years
        score = max(30.0, min(95.0, ratio * 100))
        msg = f"Candidate has {cand_years:.1f} years vs. required {req_years:.1f} years."
    else:
        score = 50.0 if not is_senior_job else 35.0
        msg = f"Specific years of experience not clearly specified in resume (target: {req_years:.1f} yrs)."

    return round(score, 1), msg


def calculate_education_score(resume_edu_text: str, job_text: str) -> tuple[float, str]:
    """Calculates 0-100 score for education requirement compatibility."""
    cand_level = detect_education_level(resume_edu_text)
    req_level = detect_education_level(job_text)

    if req_level == 0:
        # No strict degree stated
        score = 90.0 if cand_level >= 2 else 75.0
        msg = "No strict degree requirement specified by the job."
    elif cand_level >= req_level:
        score = 100.0
        msg = "Candidate education satisfies or exceeds requirements."
    elif cand_level == req_level - 1:
        score = 75.0
        msg = "Candidate possesses relevant academic background slightly below preferred credential."
    else:
        score = 50.0
        msg = "Candidate degree does not explicitly match stated requirement."

    return round(score, 1), msg


def match_resume_to_job(resume_data: dict, job_data: dict, weights: dict = None) -> dict:
    """
    Core Explainable Matching Engine:
    - Skills matching (required and preferred)
    - TF-IDF Cosine Similarity
    - Experience compatibility
    - Education compatibility
    - Weighted composite scoring
    - Actionable feedback and missing skill guidance
    """
    if weights is None:
        weights = {
            "skills": 0.50,
            "tfidf": 0.25,
            "experience": 0.15,
            "education": 0.10,
        }

    resume_text = resume_data.get("extracted_text", "")
    resume_skills = set(resume_data.get("skills", []))
    resume_exp_years = float(resume_data.get("experience_years", 0.0))
    resume_edu_info = resume_data.get("education_text", "")

    job_title = job_data.get("title", "")
    job_desc = job_data.get("description", "")
    job_exp_str = job_data.get("experience", "")
    raw_required = job_data.get("required_skills", [])
    raw_preferred = job_data.get("preferred_skills", [])

    # Normalize skill names
    if isinstance(raw_required, str):
        required_skills = [s.strip() for s in raw_required.split(",") if s.strip()]
    else:
        required_skills = [str(s).strip() for s in raw_required if str(s).strip()]

    if isinstance(raw_preferred, str):
        preferred_skills = [s.strip() for s in raw_preferred.split(",") if s.strip()]
    else:
        preferred_skills = [str(s).strip() for s in raw_preferred if str(s).strip()]

    # Case-insensitive skill matching
    resume_skills_lower = {s.lower(): s for s in resume_skills}

    matching_skills = []
    missing_skills = []

    for req in required_skills:
        req_clean = req.strip()
        if req_clean.lower() in resume_skills_lower:
            matching_skills.append(req_clean)
        else:
            missing_skills.append(req_clean)

    preferred_found = []
    for pref in preferred_skills:
        pref_clean = pref.strip()
        if pref_clean.lower() in resume_skills_lower:
            preferred_found.append(pref_clean)

    # 1. Skills Score Calculation
    total_req_count = max(len(required_skills), 1)
    base_skills_ratio = len(matching_skills) / total_req_count
    # Add modest bonus for preferred skills
    pref_bonus = min(0.15, len(preferred_found) * 0.03)
    skills_score = round(min(100.0, (base_skills_ratio + pref_bonus) * 100), 1)

    # 2. TF-IDF Text Similarity
    tfidf_result = compute_tfidf_similarity(resume_text, job_desc)
    tfidf_score = round(tfidf_result.get("percentage", 0.0), 1)

    # 3. Experience Compatibility
    exp_score, exp_feedback = calculate_experience_score(
        resume_exp_years, resume_text, job_exp_str, job_desc
    )

    # 4. Education Compatibility
    edu_score, edu_feedback = calculate_education_score(
        resume_edu_info or resume_text, job_desc
    )

    # Weighted Overall Score
    w_s = weights.get("skills", 0.50)
    w_t = weights.get("tfidf", 0.25)
    w_e = weights.get("experience", 0.15)
    w_d = weights.get("education", 0.10)

    overall = (
        skills_score * w_s
        + tfidf_score * w_t
        + exp_score * w_e
        + edu_score * w_d
    )
    overall_score = round(max(0.0, min(100.0, overall)), 1)

    # Match Category
    if overall_score >= 80.0:
        match_category = "Excellent Match"
        category_badge = "success"
    elif overall_score >= 65.0:
        match_category = "Good Match"
        category_badge = "primary"
    elif overall_score >= 45.0:
        match_category = "Moderate Match"
        category_badge = "warning"
    else:
        match_category = "Low Match"
        category_badge = "danger"

    # Actionable Improvement Recommendations
    recommendations = []

    if missing_skills:
        top_missing = missing_skills[:5]
        recommendations.append(
            f"Add concrete proof or projects for key required skills: {', '.join(top_missing)}."
        )
        for skill in top_missing:
            recommendations.append(
                f"Upskill in '{skill}': Build a hands-on GitHub project or highlight relevant coursework/certifications."
            )

    if tfidf_score < 40.0:
        recommendations.append(
            f"Align your resume keywords with the job description for '{job_title}'. "
            "Incorporate industry-standard terminology from the responsibilities section into your project summaries."
        )

    if exp_score < 70.0:
        recommendations.append(
            f"Experience gap identified ({exp_feedback}). Emphasize high-impact leadership, complex freelance work, or open-source contributions."
        )

    if not preferred_found and preferred_skills:
        recommendations.append(
            f"Consider exploring preferred skills ({', '.join(preferred_skills[:3])}) to stand out from other candidates."
        )

    if not recommendations:
        recommendations.append("Your resume aligns strongly with this position! Ensure your project bullet points quantify outcomes with metrics.")

    return {
        "overall_score": overall_score,
        "skills_score": skills_score,
        "text_similarity": tfidf_score,
        "experience_score": exp_score,
        "education_score": edu_score,
        "match_category": match_category,
        "category_badge": category_badge,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "preferred_skills_found": preferred_found,
        "shared_terms": tfidf_result.get("top_shared_terms", []),
        "recommendations": recommendations,
        "experience_feedback": exp_feedback,
        "education_feedback": edu_feedback,
        "score_breakdown": {
            "skills": {"score": skills_score, "weight": int(w_s * 100)},
            "tfidf": {"score": tfidf_score, "weight": int(w_t * 100)},
            "experience": {"score": exp_score, "weight": int(w_e * 100)},
            "education": {"score": edu_score, "weight": int(w_d * 100)},
        },
    }
