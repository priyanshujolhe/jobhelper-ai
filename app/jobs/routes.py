from flask import render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from app.jobs import jobs_bp
from app.models import Job, Resume, Analysis, SavedJob
from app.extensions import db
from app.ml.matching import match_resume_to_job
from app.jobs.recommender import recommend_jobs
from app.ml.skill_extraction import extract_skills_from_text


@jobs_bp.route("")
def index():
    query = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    emp_type = request.args.get("employment_type", "").strip()

    job_query = Job.query
    if query:
        job_query = job_query.filter(
            (Job.title.ilike(f"%{query}%")) |
            (Job.company.ilike(f"%{query}%")) |
            (Job.required_skills.ilike(f"%{query}%"))
        )
    if location:
        job_query = job_query.filter(Job.location.ilike(f"%{location}%"))
    if emp_type:
        job_query = job_query.filter(Job.employment_type == emp_type)

    jobs = job_query.order_by(Job.created_at.desc()).all()

    saved_job_ids = set()
    if current_user.is_authenticated:
        saved_jobs = SavedJob.query.filter_by(user_id=current_user.id).all()
        saved_job_ids = {sj.job_id for sj in saved_jobs}

    return render_template(
        "jobs/index.html",
        jobs=jobs,
        saved_job_ids=saved_job_ids,
        query=query,
        location=location,
        emp_type=emp_type,
    )


@jobs_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company = request.form.get("company", "").strip()
        description = request.form.get("description", "").strip()
        required_skills = request.form.get("required_skills", "").strip()
        preferred_skills = request.form.get("preferred_skills", "").strip()
        experience = request.form.get("experience", "").strip()
        location = request.form.get("location", "").strip()
        employment_type = request.form.get("employment_type", "Full-time").strip()

        if not title or not company or not description:
            flash("Please provide Job Title, Company Name, and Description.", "danger")
            return render_template("jobs/create.html")

        # If required skills left blank, auto-extract from description
        if not required_skills:
            extracted = extract_skills_from_text(description)
            required_skills = ", ".join(extracted.get("technical_skills", [])[:8])

        job = Job(
            user_id=current_user.id,
            title=title,
            company=company,
            description=description,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            experience=experience or "Not specified",
            location=location or "Remote",
            employment_type=employment_type,
            is_sample=False,
        )
        db.session.add(job)
        db.session.commit()

        flash("New job posting added successfully!", "success")
        return redirect(url_for("jobs.view_job", job_id=job.id))

    return render_template("jobs/create.html")


@jobs_bp.route("/<int:job_id>")
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    is_saved = False
    user_resumes = []

    if current_user.is_authenticated:
        is_saved = SavedJob.query.filter_by(user_id=current_user.id, job_id=job.id).first() is not None
        user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()

    return render_template("jobs/view.html", job=job, is_saved=is_saved, resumes=user_resumes)


@jobs_bp.route("/<int:job_id>/save", methods=["POST"])
@login_required
def toggle_save_job(job_id):
    job = Job.query.get_or_404(job_id)
    saved = SavedJob.query.filter_by(user_id=current_user.id, job_id=job.id).first()

    if saved:
        db.session.delete(saved)
        db.session.commit()
        flash(f"Removed '{job.title}' from your saved jobs.", "info")
    else:
        new_save = SavedJob(user_id=current_user.id, job_id=job.id)
        db.session.add(new_save)
        db.session.commit()
        flash(f"Saved '{job.title}' to your bookmarks!", "success")

    return redirect(request.referrer or url_for("jobs.index"))


@jobs_bp.route("/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        abort(403)

    db.session.delete(job)
    db.session.commit()
    flash("Job listing deleted.", "info")
    return redirect(url_for("jobs.index"))


@jobs_bp.route("/match", methods=["GET", "POST"])
@login_required
def match():
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    available_jobs = Job.query.order_by(Job.title.asc()).all()

    if not user_resumes:
        flash("Please upload a resume first before running job matching.", "warning")
        return redirect(url_for("resume.upload"))

    preselect_resume_id = request.args.get("resume_id", type=int)
    preselect_job_id = request.args.get("job_id", type=int)

    if request.method == "POST":
        resume_id = request.form.get("resume_id", type=int)
        resume = Resume.query.get_or_404(resume_id)
        if resume.user_id != current_user.id:
            abort(403)

        job_selection_type = request.form.get("job_source", "existing")

        if job_selection_type == "existing":
            job_id = request.form.get("job_id", type=int)
            job = Job.query.get_or_404(job_id)
        else:
            # User pasted custom job description
            title = request.form.get("custom_title", "Custom Job Role").strip()
            company = request.form.get("custom_company", "Confidential").strip()
            description = request.form.get("custom_description", "").strip()
            req_skills = request.form.get("custom_required_skills", "").strip()
            pref_skills = request.form.get("custom_preferred_skills", "").strip()
            experience = request.form.get("custom_experience", "Not specified").strip()
            location = request.form.get("custom_location", "Remote").strip()

            if not description:
                flash("Please enter or paste the job description.", "danger")
                return redirect(url_for("jobs.match"))

            if not req_skills:
                extracted = extract_skills_from_text(description)
                req_skills = ", ".join(extracted.get("technical_skills", [])[:6])

            job = Job(
                user_id=current_user.id,
                title=title,
                company=company,
                description=description,
                required_skills=req_skills,
                preferred_skills=pref_skills,
                experience=experience,
                location=location,
                is_sample=False,
            )
            db.session.add(job)
            db.session.flush()

        # Run ML Matching Engine
        resume_data = {
            "extracted_text": resume.extracted_text,
            "skills": resume.extracted_information.get("skills", []),
            "experience_years": resume.extracted_information.get("experience_years", 0.0),
            "education_text": resume.extracted_information.get("education_text", ""),
        }
        job_data = {
            "title": job.title,
            "description": job.description,
            "experience": job.experience,
            "required_skills": job.get_required_skills_list(),
            "preferred_skills": job.get_preferred_skills_list(),
        }

        match_result = match_resume_to_job(resume_data, job_data)

        # Store persistent analysis record
        analysis = Analysis(
            user_id=current_user.id,
            resume_id=resume.id,
            job_id=job.id,
            overall_score=match_result["overall_score"],
            skills_score=match_result["skills_score"],
            text_similarity=match_result["text_similarity"],
            experience_score=match_result["experience_score"],
            education_score=match_result["education_score"],
            match_category=match_result["match_category"],
        )
        analysis.matching_skills = match_result["matching_skills"]
        analysis.missing_skills = match_result["missing_skills"]
        analysis.preferred_skills_found = match_result["preferred_skills_found"]
        analysis.recommendations = match_result["recommendations"]

        db.session.add(analysis)
        db.session.commit()

        flash(f"Analysis completed: {match_result['overall_score']}% Match!", "success")
        return redirect(url_for("jobs.analysis_result", analysis_id=analysis.id))

    return render_template(
        "jobs/match.html",
        resumes=user_resumes,
        jobs=available_jobs,
        preselect_resume_id=preselect_resume_id,
        preselect_job_id=preselect_job_id,
    )


@jobs_bp.route("/analysis/<int:analysis_id>")
@login_required
def analysis_result(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    if analysis.user_id != current_user.id:
        abort(403)

    return render_template("jobs/analysis_result.html", analysis=analysis)


@jobs_bp.route("/recommendations")
@login_required
def recommendations():
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    if not user_resumes:
        flash("Please upload a resume first to see personalized job recommendations.", "warning")
        return redirect(url_for("resume.upload"))

    resume_id = request.args.get("resume_id", type=int)
    if resume_id:
        selected_resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        if not selected_resume:
            selected_resume = user_resumes[0]
    else:
        selected_resume = user_resumes[0]

    title_filter = request.args.get("title", "").strip()
    loc_filter = request.args.get("location", "").strip()
    emp_filter = request.args.get("employment_type", "").strip()
    exp_filter = request.args.get("experience", "").strip()
    min_score = float(request.args.get("min_score", 0.0) or 0.0)

    all_jobs = Job.query.all()
    ranked_recommendations = recommend_jobs(
        selected_resume,
        all_jobs,
        title_filter=title_filter,
        location_filter=loc_filter,
        experience_filter=exp_filter,
        employment_type_filter=emp_filter,
        min_score=min_score,
    )

    return render_template(
        "jobs/recommendations.html",
        resumes=user_resumes,
        selected_resume=selected_resume,
        recommendations=ranked_recommendations,
        title_filter=title_filter,
        loc_filter=loc_filter,
        emp_filter=emp_filter,
        exp_filter=exp_filter,
        min_score=min_score,
    )


@jobs_bp.route("/history")
@login_required
def history():
    user_analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    return render_template("jobs/history.html", analyses=user_analyses)


@jobs_bp.route("/analysis/<int:analysis_id>/delete", methods=["POST"])
@login_required
def delete_analysis(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    if analysis.user_id != current_user.id:
        abort(403)

    db.session.delete(analysis)
    db.session.commit()
    flash("Analysis record removed from your history.", "info")
    return redirect(url_for("jobs.history"))
