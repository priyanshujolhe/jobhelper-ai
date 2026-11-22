import os
import tempfile
import docx
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.resume.parser import parse_resume_file, extract_text_from_pdf, extract_text_from_docx, ResumeParseError
from app.resume.extractor import extract_resume_data
from app.resume.analyzer import evaluate_resume_quality


def create_sample_pdf(filepath: str, text: str):
    c = canvas.Canvas(filepath, pagesize=letter)
    lines = text.split("\n")
    y = 750
    for l in lines:
        c.drawString(50, y, l.strip())
        y -= 15
    c.save()


def create_sample_docx(filepath: str, text: str):
    doc = docx.Document()
    for l in text.split("\n"):
        if l.strip():
            doc.add_paragraph(l.strip())
    doc.save(filepath)


def test_pdf_resume_parsing():
    content = """Jane Doe
    Email: jane.doe@example.com | Phone: (555) 123-4567 | https://linkedin.com/in/janedoe
    Education: Bachelor of Science in Computer Science, Stanford University, 2022
    Skills: Python, Flask, SQL, React, Git, Machine Learning, Docker, PostgreSQL
    Experience: Software Engineer at Nexus Tech (2022 - Present)
    Architected RESTful microservices and optimized PostgreSQL database queries by 35% across 50,000 users.
    Developed scalable backend endpoints and reduced latency by 40% using automated caching strategies."""

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name

    try:
        create_sample_pdf(pdf_path, content)
        extracted = extract_text_from_pdf(pdf_path)

        assert "Jane Doe" in extracted
        assert "Python" in extracted
        assert "Stanford University" in extracted

        data = extract_resume_data(extracted)
        assert data["email"] == "jane.doe@example.com"
        assert "Python" in data["skills"]
        assert "Flask" in data["skills"]

        quality = evaluate_resume_quality(data, extracted)
        assert quality["total_score"] >= 60.0
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


def test_docx_resume_parsing():
    content = """Alex Smith
    alex.smith@example.org | (555) 987-6543
    Skills: JavaScript, TypeScript, React, Node.js, Docker
    Education: Master of Science in Data Analytics
    Experience: 3 years building cloud web applications."""

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        docx_path = f.name

    try:
        create_sample_docx(docx_path, content)
        extracted = extract_text_from_docx(docx_path)

        assert "Alex Smith" in extracted
        assert "TypeScript" in extracted

        data = extract_resume_data(extracted)
        assert data["email"] == "alex.smith@example.org"
        assert "React" in data["skills"]
    finally:
        if os.path.exists(docx_path):
            os.remove(docx_path)


def test_invalid_scanned_pdf_handling():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name

    try:
        # Create an empty or near-empty PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(50, 750, "")  # No text
        c.save()

        try:
            extract_text_from_pdf(pdf_path)
            assert False, "Should have raised ResumeParseError"
        except ResumeParseError as e:
            assert "sufficient text" in str(e).lower()
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
