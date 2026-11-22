import re
from app.ml.skill_extraction import extract_skills_from_text
from app.ml.matching import parse_years_of_experience, detect_education_level


# Common action verbs for resumes
ACTION_VERBS = [
    "accelerated", "accomplished", "achieved", "acquired", "adapted", "administered",
    "analyzed", "architected", "automated", "built", "centralized", "collaborated",
    "conceptualized", "constructed", "coordinated", "created", "delivered", "deployed",
    "designed", "developed", "directed", "engineered", "enhanced", "established",
    "executed", "expanded", "expedited", "fabricated", "facilitated", "formulated",
    "generated", "guided", "implemented", "improved", "increased", "initiated",
    "innovated", "installed", "integrated", "invented", "launched", "lead", "led",
    "maintained", "managed", "maximized", "mentored", "migrated", "modernized",
    "negotiated", "optimized", "orchestrated", "organized", "overhauled", "oversaw",
    "pioneered", "planned", "produced", "programmed", "reduced", "reengineered",
    "refactored", "resolved", "revamped", "scaled", "simplified", "spearheaded",
    "streamlined", "strengthened", "supervised", "trained", "transformed", "upgraded"
]

DEGREE_PATTERNS = [
    r"\b(?:bachelor(?:'s)?|b\.?s\.?c?|b\.?tech|b\.?e\.?|b\.?a\.?)\b(?:\s+in\s+[a-zA-Z\s,]+)?",
    r"\b(?:master(?:'s)?|m\.?s\.?c?|m\.?tech|m\.?e\.?|m\.?b\.?a\.?|m\.?a\.?)\b(?:\s+in\s+[a-zA-Z\s,]+)?",
    r"\b(?:ph\.?d\.?|doctorate|doctor of philosophy)\b(?:\s+in\s+[a-zA-Z\s,]+)?",
    r"\b(?:associate(?:'s)?|diploma)\b(?:\s+in\s+[a-zA-Z\s,]+)?",
]

UNIVERSITY_KEYWORDS = [
    "university", "institute", "college", "school of", "academy", "polytechnic", "faculty"
]

COMMON_LANGUAGES = [
    "English", "Spanish", "French", "German", "Mandarin", "Chinese", "Hindi",
    "Japanese", "Arabic", "Portuguese", "Russian", "Italian", "Korean", "Bengali"
]


def extract_email(text: str) -> str:
    """Extract primary contact email."""
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def extract_phone(text: str) -> str:
    """Extract contact phone number."""
    # Matches patterns like +1 (555) 123-4567, (123) 456-7890, 123-456-7890, +91 9876543210
    pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def extract_links(text: str) -> dict:
    """Extract LinkedIn, GitHub, and Portfolio URLs."""
    linkedin = ""
    github = ""
    portfolio = ""

    li_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-]+", text, re.IGNORECASE)
    if li_match:
        linkedin = li_match.group(0)

    gh_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_\-]+", text, re.IGNORECASE)
    if gh_match:
        github = gh_match.group(0)

    return {
        "linkedin": linkedin,
        "github": github,
    }


def extract_candidate_name(text: str, email: str = "") -> str:
    """
    Extract candidate name from top lines of resume text.
    Uses title case analysis and filters out headings like 'Resume', 'Curriculum Vitae'.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    ignore_words = {
        "resume", "curriculum", "vitae", "cv", "profile", "contact",
        "email", "phone", "address", "page", "skills", "summary"
    }

    for line in lines[:8]:
        # Filter line with email or url
        if "@" in line or "http" in line or "www." in line:
            continue
        cleaned = re.sub(r"[^a-zA-Z\s]", "", line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4:
            if not any(w.lower() in ignore_words for w in words):
                if all(w[0].isupper() for w in words if w):
                    return " ".join(words)

    # Fallback to email username if nothing clean found
    if email:
        username = email.split("@")[0]
        cleaned_user = re.sub(r"[0-9_.]+", " ", username).strip().title()
        if len(cleaned_user.split()) >= 2:
            return cleaned_user

    return ""


def extract_education(text: str) -> list[dict]:
    """Extracts degree, institution, and years of graduation."""
    lines = text.split("\n")
    education_entries = []

    current_entry = {}
    in_edu_section = False

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        if any(h in lower for h in ["education", "academic background", "qualifications", "academics"]):
            in_edu_section = True
            continue

        if in_edu_section and any(h in lower for h in ["experience", "employment", "skills", "projects", "certifications"]):
            break

        if in_edu_section and stripped:
            # Check for degree pattern
            degree_found = None
            for pat in DEGREE_PATTERNS:
                m = re.search(pat, stripped, re.IGNORECASE)
                if m:
                    degree_found = m.group(0).strip().title()
                    break

            # Check for institution
            has_institution = any(kw in lower for kw in UNIVERSITY_KEYWORDS)

            # Check for graduation year
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", stripped)
            grad_year = year_match.group(0) if year_match else None

            if degree_found or has_institution:
                education_entries.append({
                    "degree": degree_found or "Degree / Coursework",
                    "institution": stripped if has_institution else "Institution",
                    "year": grad_year or "",
                    "raw_text": stripped,
                })

    # If section parsing didn't find entries, search whole text for degree mentions
    if not education_entries:
        for pat in DEGREE_PATTERNS:
            for m in re.finditer(pat, text, re.IGNORECASE):
                education_entries.append({
                    "degree": m.group(0).strip().title(),
                    "institution": "University / College",
                    "year": "",
                    "raw_text": m.group(0).strip(),
                })

    return education_entries[:4]


def extract_certifications(text: str) -> list[str]:
    """Extracts professional certifications."""
    cert_list = []
    cert_keywords = [
        "AWS Certified", "Azure Certified", "Google Cloud Certified", "Cisco", "CCNA",
        "CompTIA", "PMP", "Scrum Master", "Certified Kubernetes", "TensorFlow Developer",
        "Oracle Certified", "Meta Certified"
    ]

    for line in text.split("\n"):
        lower = line.lower()
        for kw in cert_keywords:
            if kw.lower() in lower and kw not in cert_list:
                cert_list.append(kw)

    return cert_list


def extract_spoken_languages(text: str) -> list[str]:
    """Extracts spoken languages listed."""
    found = []
    lower = text.lower()
    for lang in COMMON_LANGUAGES:
        # Match "English (Fluent)", "Languages: English, Spanish"
        if re.search(rf"\b{lang.lower()}\b", lower):
            found.append(lang)
    return found


def extract_action_verbs_used(text: str) -> list[str]:
    """Finds all strong action verbs used in resume."""
    lower_words = set(re.findall(r"\b[a-z]+\b", text.lower()))
    used = [v for v in ACTION_VERBS if v in lower_words]
    return used


def extract_resume_data(text: str) -> dict:
    """
    Main extraction pipeline:
    Extracts name, email, phone, links, skills, education, certifications,
    spoken languages, action verbs, and estimates experience years.
    """
    email = extract_email(text)
    phone = extract_phone(text)
    links = extract_links(text)
    name = extract_candidate_name(text, email=email)
    skills_info = extract_skills_from_text(text)
    education = extract_education(text)
    certifications = extract_certifications(text)
    languages = extract_spoken_languages(text)
    action_verbs = extract_action_verbs_used(text)
    exp_years = parse_years_of_experience(text)
    edu_level = detect_education_level(text)

    # Format education text for matching
    edu_text = " ".join([e.get("raw_text", "") for e in education]) or text

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": links.get("linkedin", ""),
        "github": links.get("github", ""),
        "skills": skills_info.get("all_skills", []),
        "technical_skills": skills_info.get("technical_skills", []),
        "soft_skills": skills_info.get("soft_skills", []),
        "categorized_skills": skills_info.get("categorized", {}),
        "education": education,
        "education_level": edu_level,
        "education_text": edu_text,
        "certifications": certifications,
        "spoken_languages": languages,
        "action_verbs": action_verbs,
        "experience_years": exp_years,
        "word_count": len(text.split()),
        "character_count": len(text),
    }
