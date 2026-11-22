from app.models import Job
from app.extensions import db

SAMPLE_JOBS_DATA = [
    {
        "title": "Python Developer",
        "company": "Nexus Tech Solutions",
        "location": "San Francisco, CA (Hybrid)",
        "employment_type": "Full-time",
        "experience": "2+ years",
        "required_skills": "Python, Flask, SQL, REST API, Git",
        "preferred_skills": "Docker, PostgreSQL, Redis, Unit Testing",
        "description": """We are seeking a proactive Python Developer to build and scale robust backend APIs and services.
You will collaborate with cross-functional teams to design database schemas, optimize queries, and implement clean RESTful endpoints.
Responsibilities:
- Develop maintainable backend microservices using Python and modern web frameworks like Flask.
- Write performant SQL queries and maintain relational database architectures.
- Integrate third-party web APIs and asynchronous job queues.
- Participate in code reviews and automate deployments with CI/CD pipelines.
Requirements:
- Strong proficiency in Python, object-oriented design, and Flask or Django.
- Solid experience with relational databases (PostgreSQL or MySQL) and Git.
- 2+ years of professional software engineering experience.
- Bachelor's degree in Computer Science, Software Engineering, or equivalent experience."""
    },
    {
        "title": "Machine Learning Engineer",
        "company": "Cognitive AI Labs",
        "location": "New York, NY (Remote)",
        "employment_type": "Full-time",
        "experience": "3+ years",
        "required_skills": "Python, Machine Learning, Scikit-learn, TensorFlow, PyTorch, Pandas, NumPy",
        "preferred_skills": "Natural Language Processing, Docker, AWS, MLOps",
        "description": """Cognitive AI Labs is hiring a Machine Learning Engineer to design, train, and deploy production ML systems.
You will work on predictive models, natural language processing pipelines, and scalable feature engineering frameworks.
Responsibilities:
- Formulate business challenges into machine learning and predictive modeling problems.
- Preprocess unstructured and tabular datasets using Pandas, NumPy, and Scikit-learn.
- Train, evaluate, and fine-tune deep learning models using PyTorch or TensorFlow.
- Deploy models as REST microservices in containerized environments.
Requirements:
- 3+ years experience developing and deploying machine learning models.
- Deep expertise in Python, Scikit-learn, PyTorch or TensorFlow.
- Experience with NLP, feature extraction, and model evaluation metrics.
- Master's or Bachelor's in CS, Data Science, Mathematics, or related field."""
    },
    {
        "title": "Data Analyst",
        "company": "Apex Analytics Group",
        "location": "Chicago, IL (Hybrid)",
        "employment_type": "Full-time",
        "experience": "1-3 years",
        "required_skills": "SQL, Python, Pandas, Tableau, Problem Solving",
        "preferred_skills": "Power BI, Matplotlib, Statistical Modeling",
        "description": """Apex Analytics Group helps enterprise leaders turn complex data into actionable business intelligence.
We are looking for a Data Analyst to extract insights, create executive dashboards, and drive strategic decision-making.
Responsibilities:
- Write complex SQL queries across large data warehouses to aggregate business metrics.
- Build interactive visual dashboards using Tableau or Power BI.
- Clean and analyze multi-source datasets utilizing Python, Pandas, and NumPy.
- Present data narratives and strategic recommendations to leadership.
Requirements:
- 1 to 3 years experience in data analytics or business intelligence.
- Exceptional proficiency in SQL queries, joins, and aggregations.
- Experience with data visualization tools (Tableau, Power BI) and Python scripting.
- Strong analytical and communication skills."""
    },
    {
        "title": "Full Stack Web Developer",
        "company": "Vanguard Web Studio",
        "location": "Austin, TX (Remote)",
        "employment_type": "Full-time",
        "experience": "2+ years",
        "required_skills": "JavaScript, React, Node.js, HTML, CSS, REST API",
        "preferred_skills": "TypeScript, MongoDB, Tailwind CSS, Next.js",
        "description": """Join Vanguard Web Studio as a Full Stack Web Developer building responsive, high-performance web applications.
You will own feature development end-to-end, from modern React interfaces to reliable Node.js services.
Responsibilities:
- Develop responsive web user interfaces using React, HTML5, CSS3, and Tailwind.
- Architect backend RESTful services and database interactions with Node.js and Express.
- Ensure cross-browser compatibility, security, and responsive UI performance.
Requirements:
- 2+ years of experience in full-stack web application development.
- Strong knowledge of modern JavaScript (ES6+), React, and Node.js.
- Familiarity with version control using Git and agile team sprints."""
    },
    {
        "title": "Frontend Developer",
        "company": "PixelCraft Interactive",
        "location": "Seattle, WA (Remote)",
        "employment_type": "Full-time",
        "experience": "2+ years",
        "required_skills": "JavaScript, TypeScript, React, HTML, CSS, Tailwind CSS",
        "preferred_skills": "Next.js, Redux, UI/UX Design, Jest",
        "description": """PixelCraft Interactive creates consumer web experiences for millions of users worldwide.
We need a talented Frontend Developer who is passionate about pixel-perfect UI, accessibility, and smooth web performance.
Responsibilities:
- Implement rich, accessible, and responsive user interfaces using React and TypeScript.
- Translate design mockups into responsive CSS and reusable UI component libraries.
- Optimize frontend web performance, Core Web Vitals, and client-side rendering.
Requirements:
- 2+ years of dedicated frontend engineering experience.
- Deep expertise in JavaScript/TypeScript, React, HTML5, and CSS/Tailwind.
- Keen eye for UI/UX details, typography, and responsive layouts."""
    },
    {
        "title": "Backend Developer",
        "company": "CloudScale Systems",
        "location": "Denver, CO (Hybrid)",
        "employment_type": "Full-time",
        "experience": "3+ years",
        "required_skills": "Python, Django, PostgreSQL, Docker, REST API, Git",
        "preferred_skills": "Redis, AWS, Kubernetes, Microservices",
        "description": """CloudScale Systems is looking for an experienced Backend Developer to design high-throughput cloud backends.
You will be responsible for server logic, database performance, third-party integrations, and infrastructure reliability.
Responsibilities:
- Build scalable backend APIs using Python (Django or FastAPI).
- Design and optimize relational schemas in PostgreSQL.
- Containerize services with Docker and manage cloud deployment pipelines.
- Ensure high availability, data security, and API documentation.
Requirements:
- 3+ years in backend software engineering.
- Proficient in Python, Django/FastAPI, and PostgreSQL.
- Hands-on experience with Docker, Linux, and REST APIs."""
    },
    {
        "title": "Java Developer",
        "company": "Sterling Financial Tech",
        "location": "Boston, MA (On-site)",
        "employment_type": "Full-time",
        "experience": "3+ years",
        "required_skills": "Java, Spring Boot, SQL, Microservices, Git",
        "preferred_skills": "Kafka, Docker, Kubernetes, Hibernate, JUnit",
        "description": """Sterling Financial Tech powers mission-critical financial applications.
We are looking for a Java Developer to build reliable, high-volume enterprise microservices.
Responsibilities:
- Develop robust, secure enterprise microservices using Java and Spring Boot.
- Write optimized SQL queries and integrate ORM mappings with Hibernate.
- Collaborate with QA and DevOps engineers to implement comprehensive unit tests (JUnit).
Requirements:
- 3+ years experience with Java 11/17+ and Spring Boot.
- Solid understanding of OOP, design patterns, and microservices architecture.
- Experience with relational databases and SQL."""
    },
    {
        "title": "Data Scientist",
        "company": "Horizon DeepTech",
        "location": "San Jose, CA (Remote)",
        "employment_type": "Full-time",
        "experience": "2+ years",
        "required_skills": "Python, Machine Learning, Natural Language Processing, Pandas, Scikit-learn, SQL",
        "preferred_skills": "Large Language Models, Deep Learning, Cloud, PyTorch",
        "description": """Horizon DeepTech is looking for a creative Data Scientist to develop NLP models and predictive systems.
You will analyze complex datasets, build ML algorithms, and deploy intelligent features.
Responsibilities:
- Conduct statistical data analysis, hypothesis testing, and exploratory data mining.
- Build NLP and text classification models to process documents and resumes.
- Extract actionable insights and present findings to executive leadership.
Requirements:
- 2+ years of industry experience in Data Science or Applied ML.
- Proficient in Python, Pandas, Scikit-learn, and NLP methodologies.
- Master's or Bachelor's in CS, Statistics, Mathematics, or related quantitative field."""
    }
]


def seed_sample_jobs():
    """Populates the database with default sample jobs if none exist."""
    existing_count = Job.query.filter_by(is_sample=True).count()
    if existing_count > 0:
        return

    for job_info in SAMPLE_JOBS_DATA:
        job = Job(
            title=job_info["title"],
            company=job_info["company"],
            location=job_info["location"],
            employment_type=job_info["employment_type"],
            experience=job_info["experience"],
            required_skills=job_info["required_skills"],
            preferred_skills=job_info["preferred_skills"],
            description=job_info["description"],
            is_sample=True,
            user_id=None,
        )
        db.session.add(job)

    db.session.commit()
