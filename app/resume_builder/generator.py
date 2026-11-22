import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_resume_pdf(data: dict, template_name: str = "modern") -> bytes:
    """
    Generates a professional PDF resume using ReportLab.
    Supports 3 templates: 'modern', 'classic', 'minimalist'.
    Returns PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Color themes
    if template_name == "modern":
        primary_color = colors.HexColor("#1e3a8a")  # Deep blue
        accent_color = colors.HexColor("#0284c7")   # Sky blue
        text_color = colors.HexColor("#1e293b")
        font_header = "Helvetica-Bold"
    elif template_name == "minimalist":
        primary_color = colors.HexColor("#0f172a")  # Slate dark
        accent_color = colors.HexColor("#475569")
        text_color = colors.HexColor("#334155")
        font_header = "Helvetica-Bold"
    else:  # classic
        primary_color = colors.HexColor("#18181b")  # Charcoal
        accent_color = colors.HexColor("#3f3f46")
        text_color = colors.HexColor("#27272a")
        font_header = "Times-Bold"

    title_style = ParagraphStyle(
        "ResumeTitle",
        fontName=font_header,
        fontSize=22,
        leading=26,
        textColor=primary_color,
        alignment=TA_CENTER if template_name == "classic" else TA_LEFT,
    )

    subtitle_style = ParagraphStyle(
        "ResumeSubtitle",
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=accent_color,
        alignment=TA_CENTER if template_name == "classic" else TA_LEFT,
    )

    contact_style = ParagraphStyle(
        "ResumeContact",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b"),
        alignment=TA_CENTER if template_name == "classic" else TA_LEFT,
    )

    heading_style = ParagraphStyle(
        "ResumeHeading",
        fontName=font_header,
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "ResumeBody",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=text_color,
    )

    bold_body_style = ParagraphStyle(
        "ResumeBodyBold",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=text_color,
    )

    story = []

    # 1. Header: Name & Contact
    name = data.get("full_name") or data.get("name") or "Your Name"
    headline = data.get("headline", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    location = data.get("location", "")
    links = []
    if email:
        links.append(email)
    if phone:
        links.append(phone)
    if location:
        links.append(location)
    if data.get("linkedin"):
        links.append(data.get("linkedin"))
    if data.get("github"):
        links.append(data.get("github"))

    contact_line = "  •  ".join(links)

    story.append(Paragraph(name, title_style))
    if headline:
        story.append(Spacer(1, 2))
        story.append(Paragraph(headline, subtitle_style))
    if contact_line:
        story.append(Spacer(1, 4))
        story.append(Paragraph(contact_line, contact_style))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=4, spaceAfter=8))

    # 2. Professional Summary
    summary = data.get("summary") or data.get("bio")
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 6))

    # 3. Technical & Core Skills
    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    if skills:
        story.append(Paragraph("SKILLS & COMPETENCIES", heading_style))
        skill_str = ", ".join(skills)
        story.append(Paragraph(skill_str, body_style))
        story.append(Spacer(1, 6))

    # 4. Work Experience
    experiences = data.get("experience_items", [])
    if experiences:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))
        for exp in experiences:
            role = exp.get("role", "")
            company = exp.get("company", "")
            duration = exp.get("duration", "")
            desc = exp.get("description", "")

            header_text = f"<b>{role}</b> — {company}" if company else f"<b>{role}</b>"
            if duration:
                # Two column row: Title on left, dates on right
                row_table = Table(
                    [[Paragraph(header_text, bold_body_style), Paragraph(duration, ParagraphStyle("right", parent=body_style, alignment=TA_RIGHT))]],
                    colWidths=[400, 140]
                )
                row_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 1), ("TOPPADDING", (0, 0), (-1, -1), 1)]))
                story.append(row_table)
            else:
                story.append(Paragraph(header_text, bold_body_style))

            if desc:
                # Split bullet points if multi-line
                lines = [d.strip() for d in desc.split("\n") if d.strip()]
                for l in lines:
                    bullet = f"• {l.lstrip('•-* ')}"
                    story.append(Paragraph(bullet, body_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 4))

    # 5. Projects
    projects = data.get("project_items", [])
    if projects:
        story.append(Paragraph("KEY PROJECTS", heading_style))
        for proj in projects:
            title = proj.get("title", "")
            tech = proj.get("tech_stack", "")
            desc = proj.get("description", "")
            proj_header = f"<b>{title}</b>" + (f" <i>({tech})</i>" if tech else "")
            story.append(Paragraph(proj_header, bold_body_style))
            if desc:
                story.append(Paragraph(desc, body_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 4))

    # 6. Education
    education_items = data.get("education_items", [])
    if education_items:
        story.append(Paragraph("EDUCATION", heading_style))
        for edu in education_items:
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            year = edu.get("year", "")

            edu_header = f"<b>{degree}</b> — {institution}" if institution else f"<b>{degree}</b>"
            if year:
                row_table = Table(
                    [[Paragraph(edu_header, bold_body_style), Paragraph(year, ParagraphStyle("right", parent=body_style, alignment=TA_RIGHT))]],
                    colWidths=[430, 110]
                )
                row_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 1), ("TOPPADDING", (0, 0), (-1, -1), 1)]))
                story.append(row_table)
            else:
                story.append(Paragraph(edu_header, bold_body_style))
            story.append(Spacer(1, 3))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
