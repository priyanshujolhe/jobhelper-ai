import re


def evaluate_resume_quality(resume_data: dict, raw_text: str) -> dict:
    """
    Evaluates resume completeness, impact, and structure across 6 key dimensions.
    Returns:
    {
        "total_score": 85.0,
        "grade": "Strong",
        "breakdown": {
            "contact_info": {"score": 15, "max": 15, "feedback": "..."},
            "skills": {"score": 18, "max": 20, "feedback": "..."},
            "experience_impact": {"score": 15, "max": 20, "feedback": "..."},
            "education": {"score": 15, "max": 15, "feedback": "..."},
            "action_verbs": {"score": 12, "max": 15, "feedback": "..."},
            "length_structure": {"score": 15, "max": 15, "feedback": "..."}
        },
        "checklist": [...],
        "suggestions": [...]
    }
    """
    suggestions = []
    checklist = []

    # 1. Contact Information (15 pts)
    contact_score = 0
    has_email = bool(resume_data.get("email"))
    has_phone = bool(resume_data.get("phone"))
    has_links = bool(resume_data.get("linkedin") or resume_data.get("github"))

    if has_email:
        contact_score += 5
        checklist.append({"item": "Professional Email Address", "passed": True})
    else:
        suggestions.append("Add a professional email address at the top of your resume.")
        checklist.append({"item": "Professional Email Address", "passed": False})

    if has_phone:
        contact_score += 4
        checklist.append({"item": "Contact Phone Number", "passed": True})
    else:
        suggestions.append("Include a reachable phone number with your country/area code.")
        checklist.append({"item": "Contact Phone Number", "passed": False})

    if has_links:
        contact_score += 6
        checklist.append({"item": "LinkedIn / GitHub / Portfolio Link", "passed": True})
    else:
        suggestions.append("Provide a clickable link to your LinkedIn profile and active GitHub portfolio.")
        checklist.append({"item": "LinkedIn / GitHub / Portfolio Link", "passed": False})

    # 2. Skills Diversity (20 pts)
    skills_score = 0
    all_skills = resume_data.get("skills", [])
    tech_skills = resume_data.get("technical_skills", [])
    soft_skills = resume_data.get("soft_skills", [])

    if len(all_skills) >= 8:
        skills_score += 15
        checklist.append({"item": "Rich Technical & Core Skillset (8+ skills)", "passed": True})
    elif len(all_skills) >= 4:
        skills_score += 10
        checklist.append({"item": "Core Skillset Identified (4-7 skills)", "passed": True})
        suggestions.append("Expand your skills section with relevant libraries, database tools, and frameworks.")
    else:
        skills_score += 5
        checklist.append({"item": "Sufficient Skillset Identified", "passed": False})
        suggestions.append("Your resume lists very few technical keywords. Add a dedicated 'Technical Skills' section.")

    if tech_skills and soft_skills:
        skills_score += 5
        checklist.append({"item": "Balanced Technical & Collaborative Soft Skills", "passed": True})
    else:
        checklist.append({"item": "Balanced Soft & Technical Skills", "passed": False})
        suggestions.append("Incorporate collaboration or leadership skills alongside your technical proficiencies.")

    # 3. Experience & Measurable Achievements (20 pts)
    exp_score = 0
    # Search for quantifiable achievements (% increase, $ amounts, latency reduction, user scale)
    metrics_pattern = r"(?:\d+%\b|\$\d+[\d,]*|\b\d+\s*x\b|\b\d+\+?\s*(?:users|clients|customers|requests|transactions|ms|seconds|hours))"
    metric_matches = re.findall(metrics_pattern, raw_text, re.IGNORECASE)

    if len(metric_matches) >= 3:
        exp_score += 10
        checklist.append({"item": "Quantifiable Achievements & Metrics (3+ found)", "passed": True})
    elif len(metric_matches) >= 1:
        exp_score += 6
        checklist.append({"item": "Quantifiable Achievements Detected", "passed": True})
        suggestions.append("Add more specific data points (e.g. 'reduced query latency by 35%', 'scaled to 10k users').")
    else:
        checklist.append({"item": "Measurable Metrics / Outcomes", "passed": False})
        suggestions.append("Transform descriptive task lists into quantifiable achievements showing measurable impact.")

    has_exp_heading = any(k in raw_text.lower() for k in ["experience", "work history", "employment", "internship"])
    if has_exp_heading or resume_data.get("experience_years", 0) > 0:
        exp_score += 10
        checklist.append({"item": "Clearly Defined Experience / Employment Section", "passed": True})
    else:
        checklist.append({"item": "Experience Section", "passed": False})
        suggestions.append("Create a distinct 'Work Experience' or 'Project Experience' section with dates and roles.")

    # 4. Education Credentials (15 pts)
    edu_score = 0
    education_entries = resume_data.get("education", [])
    if education_entries:
        edu_score += 15
        checklist.append({"item": "Recognized Education & Academic Credentials", "passed": True})
    else:
        edu_score += 5
        checklist.append({"item": "Recognized Degree Credentials", "passed": False})
        suggestions.append("Detail your degree, major, university name, and graduation year clearly.")

    # 5. Action Verbs & Power Words (15 pts)
    verbs_score = 0
    verbs_used = resume_data.get("action_verbs", [])

    if len(verbs_used) >= 7:
        verbs_score += 15
        checklist.append({"item": "Strong Action Verbs & Dynamic Phrasing (7+ verbs)", "passed": True})
    elif len(verbs_used) >= 4:
        verbs_score += 10
        checklist.append({"item": "Good Action Verbs Found (4-6 verbs)", "passed": True})
        suggestions.append("Elevate bullet points by starting with high-impact verbs like 'Architected', 'Spearheaded', 'Optimized'.")
    else:
        verbs_score += 4
        checklist.append({"item": "Action Verbs Frequency", "passed": False})
        suggestions.append("Avoid passive phrasing like 'responsible for' or 'assisted in'; use direct action verbs.")

    # 6. Length & Readability (15 pts)
    length_score = 0
    word_count = resume_data.get("word_count", 0)

    if 350 <= word_count <= 1100:
        length_score += 15
        checklist.append({"item": f"Optimal Resume Length ({word_count} words - approx 1 to 2 pages)", "passed": True})
    elif 200 <= word_count < 350:
        length_score += 9
        checklist.append({"item": f"Resume Length ({word_count} words - somewhat brief)", "passed": True})
        suggestions.append("Your resume is brief. Expand upon your project contributions and methodologies.")
    elif 1100 < word_count <= 1800:
        length_score += 9
        checklist.append({"item": f"Resume Length ({word_count} words - moderately lengthy)", "passed": True})
        suggestions.append("Consider trimming bullet points to keep your resume concise (under 2 pages).")
    else:
        length_score += 5
        checklist.append({"item": "Optimal Resume Length", "passed": False})
        suggestions.append("Resume word count is outside the standard 1-2 page window (350-1000 words).")

    total_score = float(contact_score + skills_score + exp_score + edu_score + verbs_score + length_score)

    if total_score >= 85:
        grade = "Excellent"
        grade_badge = "success"
    elif total_score >= 70:
        grade = "Strong"
        grade_badge = "primary"
    elif total_score >= 55:
        grade = "Needs Improvement"
        grade_badge = "warning"
    else:
        grade = "Low Quality"
        grade_badge = "danger"

    return {
        "total_score": round(total_score, 1),
        "grade": grade,
        "grade_badge": grade_badge,
        "breakdown": {
            "contact_info": {"score": contact_score, "max": 15, "label": "Contact Information"},
            "skills": {"score": skills_score, "max": 20, "label": "Skills & Keywords"},
            "experience_impact": {"score": exp_score, "max": 20, "label": "Experience & Impact"},
            "education": {"score": edu_score, "max": 15, "label": "Education Credentials"},
            "action_verbs": {"score": verbs_score, "max": 15, "label": "Action-Oriented Language"},
            "length_structure": {"score": length_score, "max": 15, "label": "Length & Structure"},
        },
        "checklist": checklist,
        "suggestions": suggestions,
        "action_verbs_found": verbs_used,
        "metrics_found": metric_matches[:6],
    }
