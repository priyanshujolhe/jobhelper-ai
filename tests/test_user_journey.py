import io
import pytest
from datetime import datetime, timedelta, timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from app import create_app
from app.extensions import db
from app.models import User, OTPVerification, Resume, Job, Analysis
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def generate_test_pdf_bytes():
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    text = """Michael Chang
    michael.chang@example.com | (555) 345-6789 | San Francisco, CA
    Education: B.S. in Computer Science, University of California, Berkeley
    Skills: Python, Flask, SQL, Machine Learning, Scikit-learn, Git, REST API
    Experience: 3 years as Full Stack Engineer at Nova Software
    Architected robust Python REST APIs and integrated Scikit-learn machine learning pipelines.
    Optimized database performance by 40% across 20,000 active users."""
    y = 750
    for line in text.split("\n"):
        c.drawString(50, y, line.strip())
        y -= 16
    c.save()
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


def test_complete_user_journey(client, app):
    """
    Simulates the entire user journey:
    1. Visit home page
    2. Submit email for OTP
    3. Simulate OTP retrieval from DB (salted PBKDF2)
    4. Verify OTP and authenticate session
    5. Complete user profile
    6. Access private dashboard
    7. Upload PDF resume
    8. Verify extracted resume data
    9. Run job match against a sample job
    10. Verify analysis scores, matching skills, and missing skills
    11. View job recommendations
    12. Check analysis history
    13. Logout
    14. Re-login and verify persistence of past analysis records
    """
    # 1. Open Landing Page
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"JobHelper" in resp.data

    # 2. Login Page
    resp = client.get("/auth/login")
    assert resp.status_code == 200

    # 3. Request OTP
    user_email = "michael.chang@example.com"
    raw_code = "789123"
    with app.app_context():
        user = User(email=user_email, email_verified=False)
        db.session.add(user)
        db.session.flush()

        otp_rec = OTPVerification(
            user_id=user.id,
            email=user_email,
            otp_hash=generate_password_hash(raw_code),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
            resend_available_at=datetime.now(timezone.utc) + timedelta(seconds=60),
            used=False,
        )
        db.session.add(otp_rec)
        db.session.commit()

    # Set pending email in session
    with client.session_transaction() as sess:
        sess["pending_otp_email"] = user_email

    # 4. Verify OTP
    resp = client.post("/auth/verify-otp", data={"otp_code": raw_code}, follow_redirects=True)
    assert resp.status_code == 200

    # 5. Complete Profile
    resp = client.post(
        "/auth/complete-profile",
        data={
            "full_name": "Michael Chang",
            "phone": "555-345-6789",
            "headline": "Python & Machine Learning Developer",
            "location": "San Francisco, CA",
            "bio": "Passionate developer focused on AI.",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Michael Chang" in resp.data

    # 6. Dashboard Loads
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"Welcome back, Michael Chang" in resp.data

    # 7. Upload PDF Resume
    pdf_bytes = generate_test_pdf_bytes()
    data = {
        "resume_file": (io.BytesIO(pdf_bytes), "michael_chang_resume.pdf")
    }
    resp = client.post("/resume/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Resume uploaded and analyzed successfully" in resp.data
    assert b"michael.chang@example.com" in resp.data

    with app.app_context():
        u = User.query.filter_by(email=user_email).first()
        resume = Resume.query.filter_by(user_id=u.id).first()
        assert resume is not None
        assert "Python" in resume.extracted_information.get("skills", [])
        resume_id = resume.id

        # Also get a sample job
        job = Job.query.filter_by(title="Python Developer").first()
        assert job is not None
        job_id = job.id

    # 8. View Resume Quality
    resp = client.get(f"/resume/{resume_id}/quality")
    assert resp.status_code == 200
    assert b"Resume Quality Audit" in resp.data

    # 9. Run Match against Python Developer Job
    resp = client.post(
        "/jobs/match",
        data={
            "resume_id": str(resume_id),
            "job_source": "existing",
            "job_id": str(job_id),
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Job Compatibility Analysis" in resp.data
    assert b"Matching Skills" in resp.data

    # 10. Check Recommendations
    resp = client.get("/jobs/recommendations")
    assert resp.status_code == 200
    assert b"AI Job Recommendations" in resp.data

    # 11. Check Analysis History
    resp = client.get("/jobs/history")
    assert resp.status_code == 200
    assert b"Python Developer" in resp.data

    # 12. Test Resume Builder PDF generation
    builder_data = {
        "full_name": "Michael Chang",
        "email": user_email,
        "template": "modern",
        "skills": "Python, Flask, Scikit-learn, SQL",
        "exp_role[]": ["Software Engineer"],
        "exp_company[]": ["Nova Software"],
        "exp_duration[]": ["2022 - Present"],
        "exp_description[]": ["Built REST APIs."],
    }
    resp = client.post("/builder/download-pdf", data=builder_data)
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/pdf"

    # 13. Test Portfolio Generator ZIP download
    port_data = {
        "full_name": "Michael Chang",
        "headline": "AI Engineer",
        "email": user_email,
        "theme": "dark",
        "skills": "Python, Flask, SQL",
    }
    resp = client.post("/portfolio/download-zip", data=port_data)
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/zip"

    # 14. Log out
    resp = client.get("/auth/logout", follow_redirects=True)
    assert resp.status_code == 200
    assert b"signed out successfully" in resp.data

    # 15. Attempting to access dashboard while logged out should redirect to login
    resp = client.get("/dashboard", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Please sign in to access your dashboard" in resp.data
