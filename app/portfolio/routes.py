import io
from flask import render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from app.portfolio import portfolio_bp
from app.portfolio.generator import generate_portfolio_html, create_portfolio_zip
from app.models import Resume
from app.resume_builder.routes import extract_form_data


@portfolio_bp.route("", methods=["GET"])
@login_required
def index():
    defaults = {
        "full_name": current_user.name or "",
        "email": current_user.email or "",
        "phone": "",
        "headline": "Software Engineer & AI Enthusiast",
        "location": "",
        "bio": "Dedicated software engineer passionate about machine learning, scalable systems, and building intuitive user experiences.",
        "skills": "",
        "github": "",
        "linkedin": "",
        "theme": "dark",
        "experience_items": [],
        "project_items": [],
        "education_items": [],
    }

    if current_user.profile:
        p = current_user.profile
        defaults["full_name"] = defaults["full_name"] or p.full_name or ""
        defaults["phone"] = p.phone or defaults["phone"]
        defaults["headline"] = p.headline or defaults["headline"]
        defaults["location"] = p.location or defaults["location"]
        defaults["bio"] = p.bio or defaults["bio"]

    latest_resume = (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    if latest_resume:
        info = latest_resume.extracted_information
        if info.get("skills"):
            defaults["skills"] = ", ".join(info["skills"][:12])
        if info.get("education"):
            defaults["education_items"] = info["education"]
        if info.get("linkedin"):
            defaults["linkedin"] = info["linkedin"]
        if info.get("github"):
            defaults["github"] = info["github"]

    return render_template("portfolio/index.html", data=defaults)


@portfolio_bp.route("/preview", methods=["POST"])
@login_required
def preview():
    data = extract_form_data(request.form)
    theme = request.form.get("theme", "dark")
    html_page = generate_portfolio_html(data, theme=theme)
    # Render direct preview inside iframe or standalone
    return html_page


@portfolio_bp.route("/download-zip", methods=["POST"])
@login_required
def download_zip():
    data = extract_form_data(request.form)
    theme = request.form.get("theme", "dark")
    name = (data.get("full_name") or "portfolio").replace(" ", "_").lower()

    try:
        zip_bytes = create_portfolio_zip(data, theme=theme)
        return send_file(
            io.BytesIO(zip_bytes),
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{name}_portfolio.zip",
        )
    except Exception as e:
        flash(f"Error creating portfolio zip: {str(e)}", "danger")
        return redirect(url_for("portfolio.index"))
