import re

# Comprehensive canonical taxonomy of skills with aliases
SKILL_TAXONOMY = {
    # Programming Languages
    "Python": ["python", "py"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "Java": ["java", "core java", "j2ee"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp", "c-sharp"],
    "C": ["c language", "embedded c"],
    "Go": ["golang", "go language"],
    "Rust": ["rust", "rustlang"],
    "PHP": ["php", "php7", "php8"],
    "Ruby": ["ruby"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],
    "R": ["r language", "r programming"],
    "MATLAB": ["matlab"],
    "Scala": ["scala"],
    "Dart": ["dart"],
    "SQL": ["sql", "structured query language"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Bash": ["bash", "shell scripting", "sh"],

    # Web & Backend Frameworks
    "Flask": ["flask"],
    "Django": ["django", "django rest framework", "drf"],
    "FastAPI": ["fastapi"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular", "angularjs", "angular 2+"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Next.js": ["next.js", "nextjs"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Express.js": ["express", "express.js", "expressjs"],
    "Spring Boot": ["spring boot", "springboot", "spring framework"],
    "ASP.NET": ["asp.net", "asp.net core", ".net core", "dotnet"],
    "Ruby on Rails": ["rails", "ruby on rails"],
    "Laravel": ["laravel"],
    "Tailwind CSS": ["tailwind", "tailwind css", "tailwindcss"],
    "Bootstrap": ["bootstrap", "bootstrap 5"],
    "GraphQL": ["graphql"],
    "REST API": ["rest api", "restful api", "restful web services", "rest apis"],

    # Machine Learning & AI & Data Science
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "dl"],
    "Natural Language Processing": ["natural language processing", "nlp"],
    "Computer Vision": ["computer vision", "cv", "opencv"],
    "Large Language Models": ["llm", "llms", "large language models", "prompt engineering", "langchain"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow", "tf"],
    "PyTorch": ["pytorch", "torch"],
    "Keras": ["keras"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "SciPy": ["scipy"],
    "Matplotlib": ["matplotlib"],
    "Seaborn": ["seaborn"],
    "Tableau": ["tableau"],
    "Power BI": ["power bi", "powerbi"],
    "Apache Spark": ["spark", "apache spark", "pyspark"],
    "Hadoop": ["hadoop", "apache hadoop"],

    # Cloud & DevOps
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud Platform": ["gcp", "google cloud", "google cloud platform"],
    "Docker": ["docker", "containerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
    "Jenkins": ["jenkins"],
    "GitHub Actions": ["github actions"],
    "Terraform": ["terraform"],
    "Linux": ["linux", "ubuntu", "centos", "debian"],
    "Nginx": ["nginx"],
    "Git": ["git", "github", "gitlab", "version control"],

    # Databases & Storage
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "SQLite": ["sqlite", "sqlite3"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "Cassandra": ["cassandra", "apache cassandra"],
    "Elasticsearch": ["elasticsearch"],
    "Oracle Database": ["oracle db", "oracle database"],
    "Firebase": ["firebase", "firestore"],

    # Methodologies & Architecture
    "Microservices": ["microservices", "microservice architecture"],
    "Agile": ["agile", "scrum", "sprints", "kanban"],
    "Test-Driven Development": ["tdd", "test driven development", "unit testing", "pytest"],
    "System Design": ["system design", "software architecture"],

    # Soft Skills
    "Problem Solving": ["problem solving", "analytical thinking", "critical thinking"],
    "Communication": ["communication skills", "effective communication", "verbal communication"],
    "Team Leadership": ["leadership", "team leadership", "mentorship"],
    "Collaboration": ["collaboration", "cross-functional collaboration", "teamwork"],
    "Time Management": ["time management", "prioritization", "multitasking"],
    "Adaptability": ["adaptability", "quick learner", "flexibility"],
}

# Categorization mapping
SKILL_CATEGORIES = {
    "Programming Languages": {
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go",
        "Rust", "PHP", "Ruby", "Swift", "Kotlin", "R", "MATLAB", "Scala", "Dart",
        "SQL", "HTML", "CSS", "Bash"
    },
    "Frameworks & Web": {
        "Flask", "Django", "FastAPI", "React", "Angular", "Vue.js", "Next.js",
        "Node.js", "Express.js", "Spring Boot", "ASP.NET", "Ruby on Rails",
        "Laravel", "Tailwind CSS", "Bootstrap", "GraphQL", "REST API"
    },
    "AI, ML & Data Science": {
        "Machine Learning", "Deep Learning", "Natural Language Processing",
        "Computer Vision", "Large Language Models", "Scikit-learn", "TensorFlow",
        "PyTorch", "Keras", "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn",
        "Tableau", "Power BI", "Apache Spark", "Hadoop"
    },
    "Cloud & DevOps": {
        "AWS", "Azure", "Google Cloud Platform", "Docker", "Kubernetes",
        "CI/CD", "Jenkins", "GitHub Actions", "Terraform", "Linux", "Nginx", "Git"
    },
    "Databases": {
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra",
        "Elasticsearch", "Oracle Database", "Firebase"
    },
    "Soft Skills": {
        "Problem Solving", "Communication", "Team Leadership", "Collaboration",
        "Time Management", "Adaptability"
    }
}


def extract_skills_from_text(text: str) -> dict:
    """
    Extracts skills using boundary-safe regex matching across the canonical taxonomy.
    Returns:
    {
        "all_skills": ["Python", "Flask", ...],
        "technical_skills": ["Python", "Flask", ...],
        "soft_skills": ["Problem Solving", ...],
        "categorized": {
            "Programming Languages": ["Python", ...],
            ...
        }
    }
    """
    if not text:
        return {
            "all_skills": [],
            "technical_skills": [],
            "soft_skills": [],
            "categorized": {cat: [] for cat in SKILL_CATEGORIES}
        }

    # Normalize text for matching
    lower_text = text.lower()
    # Normalize internal separators for easier matching
    normalized_for_search = re.sub(r"[\t\r\n/]", " ", lower_text)

    matched_canonical = set()

    for canonical, aliases in SKILL_TAXONOMY.items():
        found = False
        for alias in aliases:
            # Handle special symbols like C++, C#, .NET
            if alias in {"c++", "c#"}:
                escaped = re.escape(alias)
                pattern = rf"(?:^|[^\w\+])({escaped})(?:[^\w\+]|$)"
            elif alias in {"c"}:
                # Single letter 'c' requires strict context: "c programming" or "c / c++"
                pattern = r"(?:^|\s)(?:c\s*(?:language|programming|\/|\,))\b"
            elif alias in {"r"}:
                pattern = r"(?:^|\s)(?:r\s*(?:language|programming|studio))\b"
            else:
                escaped = re.escape(alias)
                pattern = rf"\b{escaped}\b"

            if re.search(pattern, normalized_for_search):
                matched_canonical.add(canonical)
                found = True
                break

    categorized = {cat: [] for cat in SKILL_CATEGORIES}
    technical_skills = []
    soft_skills = []

    for skill in sorted(matched_canonical):
        is_soft = skill in SKILL_CATEGORIES.get("Soft Skills", set())
        if is_soft:
            soft_skills.append(skill)
            categorized["Soft Skills"].append(skill)
        else:
            technical_skills.append(skill)
            for cat, skill_set in SKILL_CATEGORIES.items():
                if cat != "Soft Skills" and skill in skill_set:
                    categorized[cat].append(skill)

    return {
        "all_skills": sorted(matched_canonical),
        "technical_skills": technical_skills,
        "soft_skills": soft_skills,
        "categorized": categorized
    }
