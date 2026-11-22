import json
from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    profile = db.relationship("UserProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    resumes = db.relationship("Resume", backref="user", lazy=True, cascade="all, delete-orphan")
    analyses = db.relationship("Analysis", backref="user", lazy=True, cascade="all, delete-orphan")
    jobs = db.relationship("Job", backref="author", lazy=True, cascade="all, delete-orphan")
    saved_jobs = db.relationship("SavedJob", backref="user", lazy=True, cascade="all, delete-orphan")
    otp_verifications = db.relationship("OTPVerification", backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class OTPVerification(db.Model):
    __tablename__ = "otp_verifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    resend_available_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def is_expired(self):
        now = datetime.now(timezone.utc)
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return now > exp

    def can_resend(self):
        now = datetime.now(timezone.utc)
        resend_time = self.resend_available_at
        if resend_time.tzinfo is None:
            resend_time = resend_time.replace(tzinfo=timezone.utc)
        return now >= resend_time


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    headline = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size_bytes = db.Column(db.Integer, default=0)
    extracted_text = db.Column(db.Text, nullable=False)
    _extracted_information = db.Column("extracted_information", db.Text, nullable=False, default="{}")
    quality_score = db.Column(db.Float, default=0.0)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    analyses = db.relationship("Analysis", backref="resume", lazy=True, cascade="all, delete-orphan")

    @property
    def extracted_information(self):
        try:
            return json.loads(self._extracted_information)
        except Exception:
            return {}

    @extracted_information.setter
    def extracted_information(self, value):
        self._extracted_information = json.dumps(value, ensure_ascii=False)


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)  # Comma-separated or JSON
    preferred_skills = db.Column(db.Text, nullable=True)
    experience = db.Column(db.String(100), nullable=True)  # e.g., "2+ years", "Mid-Level"
    location = db.Column(db.String(150), nullable=True)
    employment_type = db.Column(db.String(50), default="Full-time")  # Full-time, Part-time, Remote, etc.
    is_sample = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    analyses = db.relationship("Analysis", backref="job", lazy=True, cascade="all, delete-orphan")
    saved_by = db.relationship("SavedJob", backref="job", lazy=True, cascade="all, delete-orphan")

    def get_required_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(",") if s.strip()]

    def get_preferred_skills_list(self):
        if not self.preferred_skills:
            return []
        return [s.strip() for s in self.preferred_skills.split(",") if s.strip()]


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "job_id", name="unique_user_saved_job"),)


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    overall_score = db.Column(db.Float, nullable=False)
    skills_score = db.Column(db.Float, nullable=False)
    text_similarity = db.Column(db.Float, nullable=False)
    experience_score = db.Column(db.Float, default=0.0)
    education_score = db.Column(db.Float, default=0.0)

    _matching_skills = db.Column("matching_skills", db.Text, nullable=False, default="[]")
    _missing_skills = db.Column("missing_skills", db.Text, nullable=False, default="[]")
    _preferred_skills_found = db.Column("preferred_skills_found", db.Text, nullable=True, default="[]")
    _recommendations = db.Column("recommendations", db.Text, nullable=False, default="[]")
    match_category = db.Column(db.String(50), nullable=True)  # Excellent Match, Good Match, etc.

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @property
    def matching_skills(self):
        try:
            return json.loads(self._matching_skills)
        except Exception:
            return []

    @matching_skills.setter
    def matching_skills(self, value):
        self._matching_skills = json.dumps(value, ensure_ascii=False)

    @property
    def missing_skills(self):
        try:
            return json.loads(self._missing_skills)
        except Exception:
            return []

    @missing_skills.setter
    def missing_skills(self, value):
        self._missing_skills = json.dumps(value, ensure_ascii=False)

    @property
    def preferred_skills_found(self):
        try:
            return json.loads(self._preferred_skills_found or "[]")
        except Exception:
            return []

    @preferred_skills_found.setter
    def preferred_skills_found(self, value):
        self._preferred_skills_found = json.dumps(value, ensure_ascii=False)

    @property
    def recommendations(self):
        try:
            return json.loads(self._recommendations)
        except Exception:
            return []

    @recommendations.setter
    def recommendations(self, value):
        self._recommendations = json.dumps(value, ensure_ascii=False)
