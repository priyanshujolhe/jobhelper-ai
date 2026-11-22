from app.models import Job, Resume
from app.ml.matching import match_resume_to_job


def recommend_jobs(
    resume: Resume,
    jobs: list[Job],
    title_filter: str = "",
    location_filter: str = "",
    experience_filter: str = "",
    employment_type_filter: str = "",
    min_score: float = 0.0,
) -> list[dict]:
    """
    Ranks jobs for the specified resume by multi-dimensional compatibility score.
    Applies search and attribute filters.
    """
    resume_data = {
        "extracted_text": resume.extracted_text,
        "skills": resume.extracted_information.get("skills", []),
        "experience_years": resume.extracted_information.get("experience_years", 0.0),
        "education_text": resume.extracted_information.get("education_text", ""),
    }

    results = []

    for job in jobs:
        # Title filter
        if title_filter and title_filter.lower() not in job.title.lower():
            continue

        # Location filter
        if location_filter and location_filter.lower() not in (job.location or "").lower():
            continue

        # Employment type filter
        if employment_type_filter and employment_type_filter.lower() not in (job.employment_type or "").lower():
            continue

        # Experience level filter
        if experience_filter and experience_filter.lower() not in (job.experience or "").lower():
            continue

        job_data = {
            "title": job.title,
            "description": job.description,
            "experience": job.experience,
            "required_skills": job.get_required_skills_list(),
            "preferred_skills": job.get_preferred_skills_list(),
        }

        match_res = match_resume_to_job(resume_data, job_data)
        overall_score = match_res["overall_score"]

        if overall_score < min_score:
            continue

        results.append({
            "job": job,
            "overall_score": overall_score,
            "skills_score": match_res["skills_score"],
            "text_similarity": match_res["text_similarity"],
            "experience_score": match_res["experience_score"],
            "match_category": match_res["match_category"],
            "category_badge": match_res["category_badge"],
            "matching_skills": match_res["matching_skills"],
            "missing_skills": match_res["missing_skills"],
            "recommendations": match_res["recommendations"],
        })

    # Sort descending by overall match score
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results
