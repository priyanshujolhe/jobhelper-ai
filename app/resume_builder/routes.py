import io
from flask import render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from app.resume_builder import builder_bp
from app.resume_builder.generator import generate_resume_pdf
from app.models import Resume


def extract_form_data(form) -> dict:
    # Basic info
    full_name = form.get("full_name", "").strip()
    headline = form.get("headline", "").strip()
    email = form.get("email", "").strip()
    phone = form.get("phone", "").strip()
    location = form.get("location", "").strip()
    linkedin = form.get("linkedin", "").strip()
    github = form.get("github", "").strip()
    summary = form.get("summary", "").strip()
    skills_raw = form.get("skills", "").strip()
    template_name = form.get("template", "modern").strip()

    skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

    # Experiences (dynamic form fields)
    exp_roles = form.getlist("exp_role[]")
    exp_companies = form.getlist("exp_company[]")
    exp_durations = form.getlist("exp_duration[]")
    exp_descriptions = form.getlist("exp_description[]")

    experience_items = []
    for i in range(len(exp_roles)):
        if exp_roles[i].strip():
            experience_items.append({
                "role": exp_roles[i].strip(),
                "company": exp_companies[i].strip() if i < len(exp_companies) else "",
                "duration": exp_durations[i].strip() if i < len(exp_durations) else "",
                "description": exp_descriptions[i].strip() if i < len(exp_descriptions) else "",
            })

    # Projects
    proj_titles = form.getlist("proj_title[]")
    proj_techs = form.getlist("proj_tech[]")
    proj_descriptions = form.getlist("proj_description[]")

    project_items = []
    for i in range(len(proj_titles)):
        if proj_titles[i].strip():
            project_items.append({
                "title": proj_titles[i].strip(),
                "tech_stack": proj_techs[i].strip() if i < len(proj_techs) else "",
                "description": proj_descriptions[i].strip() if i < len(proj_descriptions) else "",
            })

    # Education
    edu_degrees = form.getlist("edu_degree[]")
    edu_institutions = form.getlist("edu_institution[]")
    edu_years = form.getlist("edu_year[]")

    education_items = []
    for i in range(len(edu_degrees)):
        if edu_degrees[i].strip():
            education_items.append({
                "degree": edu_degrees[i].strip(),
                "institution": edu_institutions[i].strip() if i < len(edu_institutions) else "",
                "year": edu_years[i].strip() if i < len(edu_years) else "",
            })

    return {
        "full_name": full_name,
        "headline": headline,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "summary": summary,
        "skills": skills,
        "experience_items": experience_items,
        "project_items": project_items,
        "education_items": education_items,
        "template": template_name,
    }


@builder_bp.route("", methods=["GET"])
@login_required
def index():
    # Pre-populate with user profile or latest uploaded resume
    defaults = {
        "full_name": current_user.name or "",
        "email": current_user.email or "",
        "phone": "",
        "headline": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "summary": "",
        "skills": "",
        "template": "modern",
        "experience_items": [],
        "project_items": [],
        "education_items": [],
    }

    if current_user.profile:
        p = current_user.profile
        defaults["full_name"] = defaults["full_name"] or p.full_name or ""
        defaults["phone"] = p.phone or ""
        defaults["headline"] = p.headline or ""
        defaults["location"] = p.location or ""
        defaults["summary"] = p.bio or ""

    latest_resume = (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    if latest_resume:
        info = latest_resume.extracted_information
        if not defaults["phone"] and info.get("phone"):
            defaults["phone"] = info["phone"]
        if not defaults["linkedin"] and info.get("linkedin"):
            defaults["linkedin"] = info["linkedin"]
        if not defaults["github"] and info.get("github"):
            defaults["github"] = info["github"]
        if info.get("skills"):
            defaults["skills"] = ", ".join(info["skills"][:15])
        if info.get("education"):
            defaults["education_items"] = info["education"]

    return render_template("builder/index.html", data=defaults)


@builder_bp.route("/preview", methods=["POST"])
@login_required
def preview():
    data = extract_form_data(request.form)
    return render_template("builder/preview.html", data=data, template_name=data.get("template", "modern"))


@builder_bp.route("/download-pdf", methods=["POST"])
@login_required
def download_pdf():
    data = extract_form_data(request.form)
    template_name = data.get("template", "modern")

    try:
        pdf_bytes = generate_resume_pdf(data, template_name=template_name)
        safe_name = (data.get("full_name") or "resume").replace(" ", "_").lower()
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{safe_name}_resume.pdf",
        )
    except Exception as e:
        flash(f"Error generating PDF: {str(e)}", "danger")
        return redirect(url_for("builder.index"))
