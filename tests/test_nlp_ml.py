from app.ml.preprocessing import clean_text, tokenize, remove_stopwords, preprocess_text
from app.ml.skill_extraction import extract_skills_from_text
from app.ml.feature_extraction import compute_tfidf_similarity
from app.ml.matching import match_resume_to_job, parse_years_of_experience, detect_education_level


def test_text_cleaning_and_tokenization():
    raw_html = "<p>Experienced software engineer proficient in <b>Python</b>, C++, and Node.js.</p>"
    cleaned = clean_text(raw_html)
    assert "<p>" not in cleaned
    assert "<b>" not in cleaned
    assert "Python" in cleaned

    tokens = tokenize(cleaned)
    assert "c++" in tokens
    assert "node.js" in tokens
    assert "python" in tokens


def test_skill_extraction():
    sample_text = """
    Software Engineer with expertise in Python, Flask, SQL, React, Docker, and AWS.
    Strong analytical and problem solving skills. Familiar with REST API architectures and Git.
    """
    skills_data = extract_skills_from_text(sample_text)
    all_skills = skills_data["all_skills"]

    assert "Python" in all_skills
    assert "Flask" in all_skills
    assert "SQL" in all_skills
    assert "React" in all_skills
    assert "Docker" in all_skills
    assert "AWS" in all_skills
    assert "Problem Solving" in all_skills
    assert "REST API" in all_skills
    assert "Git" in all_skills

    # Verify categorization
    assert "Python" in skills_data["categorized"]["Programming Languages"]
    assert "Docker" in skills_data["categorized"]["Cloud & DevOps"]
    assert "Problem Solving" in skills_data["soft_skills"]


def test_tfidf_cosine_similarity():
    text_a = "Senior Python developer experienced with Flask microservices and PostgreSQL databases."
    text_b = "Looking for a Python software engineer to develop Flask web services and manage SQL databases."
    text_unrelated = "Pastry chef specializing in french croissants and artisan chocolate desserts."

    sim_related = compute_tfidf_similarity(text_a, text_b)
    sim_unrelated = compute_tfidf_similarity(text_a, text_unrelated)

    assert sim_related["percentage"] > 5.0
    assert sim_related["percentage"] > sim_unrelated["percentage"]
    assert sim_unrelated["percentage"] == 0.0
    assert any("python" in term for term in sim_related["top_shared_terms"])


def test_matching_algorithm_scoring():
    resume_data = {
        "extracted_text": "Python developer with 3 years experience building Flask APIs and PostgreSQL apps. BS in Computer Science.",
        "skills": ["Python", "Flask", "SQL", "PostgreSQL", "Git"],
        "experience_years": 3.0,
        "education_text": "Bachelor of Science in Computer Science",
    }

    job_data = {
        "title": "Python Developer",
        "description": "Looking for a Python Developer with Flask and SQL experience. 2+ years experience.",
        "experience": "2+ years",
        "required_skills": ["Python", "Flask", "SQL", "Docker"],
        "preferred_skills": ["PostgreSQL", "AWS"],
    }

    result = match_resume_to_job(resume_data, job_data)

    assert "Python" in result["matching_skills"]
    assert "Flask" in result["matching_skills"]
    assert "SQL" in result["matching_skills"]
    assert "Docker" in result["missing_skills"]
    assert "PostgreSQL" in result["preferred_skills_found"]

    # Overall score should be solid (meets 3/4 required skills, meets exp, meets edu)
    assert 60.0 <= result["overall_score"] <= 100.0
    assert result["match_category"] in {"Good Match", "Excellent Match"}
    assert len(result["recommendations"]) > 0


def test_experience_and_education_detection():
    text1 = "Worked as a developer for 4+ years at Tech Corp. Master's in Artificial Intelligence."
    years = parse_years_of_experience(text1)
    edu_level = detect_education_level(text1)

    assert years == 4.0
    assert edu_level == 3  # Master's degree
