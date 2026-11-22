from collections import Counter
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.dashboard import dashboard_bp
from app.models import Resume, Job, Analysis, SavedJob, UserProfile
from app.extensions import db
from app.jobs.recommender import recommend_jobs
from app.ml.skill_extraction import SKILL_CATEGORIES


@dashboard_bp.route("")
@login_required
def index():
    user_id = current_user.id

    # 1. Database-backed statistics
    resumes_count = Resume.query.filter_by(user_id=user_id).count()
    analyses_count = Analysis.query.filter_by(user_id=user_id).count()
    saved_jobs_count = SavedJob.query.filter_by(user_id=user_id).count()

    avg_score_val = (
        db.session.query(db.func.avg(Analysis.overall_score))
        .filter(Analysis.user_id == user_id)
        .scalar()
    )
    avg_match_score = round(float(avg_score_val), 1) if avg_score_val else 0.0

    # 2. Gather user's resumes and extracted skills
    user_resumes = (
        Resume.query.filter_by(user_id=user_id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    )

    all_user_skills = set()
    category_counts = {cat: 0 for cat in SKILL_CATEGORIES}

    for r in user_resumes:
        skills = r.extracted_information.get("skills", [])
        all_user_skills.update(skills)

        for s in skills:
            for cat, cset in SKILL_CATEGORIES.items():
                if s in cset:
                    category_counts[cat] += 1

    skills_count = len(all_user_skills)

    # 3. Recent Analyses (last 5)
    recent_analyses = (
        Analysis.query.filter_by(user_id=user_id)
        .order_by(Analysis.created_at.desc())
        .limit(5)
        .all()
    )

    # 4. Top Recommended Jobs (using latest resume if exists)
    top_recommendations = []
    latest_resume = user_resumes[0] if user_resumes else None
    if latest_resume:
        all_jobs = Job.query.all()
        top_recommendations = recommend_jobs(latest_resume, all_jobs)[:4]

    # 5. Chart data for Chart.js (Skill Distribution by Category)
    chart_labels = list(category_counts.keys())
    chart_values = list(category_counts.values())

    return render_template(
        "dashboard/index.html",
        resumes_count=resumes_count,
        analyses_count=analyses_count,
        saved_jobs_count=saved_jobs_count,
        avg_match_score=avg_match_score,
        skills_count=skills_count,
        recent_analyses=recent_analyses,
        latest_resume=latest_resume,
        top_recommendations=top_recommendations,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


@dashboard_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_profile = current_user.profile
    if not user_profile:
        user_profile = UserProfile(user_id=current_user.id)
        db.session.add(user_profile)
        db.session.commit()

    if request.method == "POST":
        current_user.name = request.form.get("name", "").strip()
        user_profile.full_name = current_user.name
        user_profile.phone = request.form.get("phone", "").strip()
        user_profile.headline = request.form.get("headline", "").strip()
        user_profile.location = request.form.get("location", "").strip()
        user_profile.bio = request.form.get("bio", "").strip()
        user_profile.education = request.form.get("education", "").strip()
        user_profile.experience = request.form.get("experience", "").strip()

        db.session.commit()
        flash("Your profile was updated successfully!", "success")
        return redirect(url_for("dashboard.profile"))

    return render_template("dashboard/profile.html", profile=user_profile)


@dashboard_bp.route("/settings")
@login_required
def settings():
    return render_template("dashboard/settings.html")
