import os
import uuid
from pathlib import Path
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.resume import resume_bp
from app.resume.parser import parse_resume_file, ResumeParseError
from app.resume.extractor import extract_resume_data
from app.resume.analyzer import evaluate_resume_quality
from app.models import Resume, Job
from app.extensions import db


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@resume_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if "resume_file" not in request.files:
            flash("No file part in the request.", "danger")
            return redirect(request.url)

        file = request.files["resume_file"]
        if not file or file.filename == "":
            flash("Please select a resume file to upload.", "warning")
            return redirect(request.url)

        if not is_allowed_file(file.filename):
            flash("Invalid file format. Only PDF and DOCX files are allowed.", "danger")
            return redirect(request.url)

        orig_filename = secure_filename(file.filename)
        file_ext = Path(orig_filename).suffix.lower()

        # Check file size (5MB limit)
        file.seek(0, os.SEEK_END)
        size_bytes = file.tell()
        file.seek(0)
        max_bytes = current_app.config.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)

        if size_bytes > max_bytes:
            flash("File is too large. Maximum allowed file size is 5 MB.", "danger")
            return redirect(request.url)

        # Ensure upload folder exists
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        stored_filename = f"{uuid.uuid4().hex}_{orig_filename}"
        saved_path = os.path.join(upload_folder, stored_filename)
        file.save(saved_path)

        # Parse text from file
        try:
            raw_text = parse_resume_file(saved_path)
        except ResumeParseError as e:
            if os.path.exists(saved_path):
                os.remove(saved_path)
            flash(str(e), "danger")
            return redirect(request.url)

        # Extract structured data
        extracted_info = extract_resume_data(raw_text)

        # Evaluate quality score
        quality_eval = evaluate_resume_quality(extracted_info, raw_text)
        quality_score = quality_eval.get("total_score", 0.0)

        # Create database record
        resume = Resume(
            user_id=current_user.id,
            original_filename=orig_filename,
            stored_filename=stored_filename,
            file_type=file_ext.replace(".", "").upper(),
            file_size_bytes=size_bytes,
            extracted_text=raw_text,
            quality_score=quality_score,
        )
        resume.extracted_information = extracted_info

        db.session.add(resume)
        db.session.commit()

        flash("Resume uploaded and analyzed successfully!", "success")
        return redirect(url_for("resume.view", resume_id=resume.id))

    # GET: show upload page with list of user's uploaded resumes
    user_resumes = (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    )
    return render_template("resume/upload.html", resumes=user_resumes)


@resume_bp.route("/<int:resume_id>")
@login_required
def view(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)

    extracted = resume.extracted_information
    # Also fetch available jobs for quick match CTA
    sample_jobs = Job.query.limit(5).all()

    return render_template("resume/analysis.html", resume=resume, data=extracted, sample_jobs=sample_jobs)


@resume_bp.route("/<int:resume_id>/quality")
@login_required
def quality(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)

    extracted = resume.extracted_information
    quality_eval = evaluate_resume_quality(extracted, resume.extracted_text)

    return render_template(
        "resume/quality.html",
        resume=resume,
        data=extracted,
        quality=quality_eval,
    )


@resume_bp.route("/<int:resume_id>/update", methods=["POST"])
@login_required
def update(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)

    info = resume.extracted_information

    # Allow user to edit name, email, phone, and skills
    info["name"] = request.form.get("name", info.get("name", "")).strip()
    info["email"] = request.form.get("email", info.get("email", "")).strip()
    info["phone"] = request.form.get("phone", info.get("phone", "")).strip()
    info["linkedin"] = request.form.get("linkedin", info.get("linkedin", "")).strip()
    info["github"] = request.form.get("github", info.get("github", "")).strip()

    skills_raw = request.form.get("skills", "")
    if skills_raw:
        skill_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
        info["skills"] = skill_list
        info["technical_skills"] = skill_list

    exp_str = request.form.get("experience_years", "")
    if exp_str:
        try:
            info["experience_years"] = float(exp_str)
        except ValueError:
            pass

    resume.extracted_information = info
    # Re-evaluate quality score
    quality_eval = evaluate_resume_quality(info, resume.extracted_text)
    resume.quality_score = quality_eval.get("total_score", 0.0)

    db.session.commit()
    flash("Resume details updated successfully!", "success")
    return redirect(url_for("resume.view", resume_id=resume.id))


@resume_bp.route("/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)

    # Remove stored physical file if exists
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, resume.stored_filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

    db.session.delete(resume)
    db.session.commit()
    flash("Resume deleted successfully.", "info")
    return redirect(url_for("resume.upload"))
