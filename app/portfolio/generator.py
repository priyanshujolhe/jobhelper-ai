import io
import zipfile
import html


def sanitize(val: str) -> str:
    """Escapes user input to prevent XSS in generated portfolios."""
    return html.escape(str(val or ""))


def generate_portfolio_html(data: dict, theme: str = "dark") -> str:
    name = sanitize(data.get("full_name") or "Alex Morgan")
    headline = sanitize(data.get("headline") or "Software Engineer & AI Enthusiast")
    bio = sanitize(data.get("bio") or "Passionate developer dedicated to building impactful digital products.")
    email = sanitize(data.get("email") or "")
    phone = sanitize(data.get("phone") or "")
    location = sanitize(data.get("location") or "")
    github = sanitize(data.get("github") or "")
    linkedin = sanitize(data.get("linkedin") or "")

    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]

    experiences = data.get("experience_items", [])
    projects = data.get("project_items", [])
    education = data.get("education_items", [])

    # Theme CSS tokens
    if theme == "light":
        bg_main = "#f8fafc"
        bg_card = "#ffffff"
        text_primary = "#0f172a"
        text_muted = "#64748b"
        accent_color = "#2563eb"
        border_color = "#e2e8f0"
        hero_bg = "linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%)"
    elif theme == "gradient":
        bg_main = "#090d16"
        bg_card = "rgba(18, 24, 38, 0.7)"
        text_primary = "#f1f5f9"
        text_muted = "#94a3b8"
        accent_color = "#8b5cf6"
        border_color = "rgba(139, 92, 246, 0.2)"
        hero_bg = "linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%)"
    else:  # dark
        bg_main = "#0b0f17"
        bg_card = "#111827"
        text_primary = "#f9fafb"
        text_muted = "#9ca3af"
        accent_color = "#38bdf8"
        border_color = "#1f2937"
        hero_bg = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"

    skills_html = "".join([f'<span class="skill-tag">{sanitize(s)}</span>' for s in skills])

    exp_html = ""
    for exp in experiences:
        role = sanitize(exp.get("role", ""))
        comp = sanitize(exp.get("company", ""))
        dur = sanitize(exp.get("duration", ""))
        desc = sanitize(exp.get("description", ""))
        exp_html += f"""
        <div class="timeline-item">
            <div class="timeline-header">
                <h3>{role}</h3>
                <span class="badge">{dur}</span>
            </div>
            <div class="company">{comp}</div>
            <p>{desc.replace(chr(10), '<br>')}</p>
        </div>"""

    proj_html = ""
    for proj in projects:
        title = sanitize(proj.get("title", ""))
        tech = sanitize(proj.get("tech_stack", ""))
        desc = sanitize(proj.get("description", ""))
        proj_html += f"""
        <div class="project-card">
            <div class="project-header">
                <h3>{title}</h3>
                <span class="project-tech">{tech}</span>
            </div>
            <p>{desc}</p>
        </div>"""

    edu_html = ""
    for edu in education:
        deg = sanitize(edu.get("degree", ""))
        inst = sanitize(edu.get("institution", ""))
        yr = sanitize(edu.get("year", ""))
        edu_html += f"""
        <div class="timeline-item">
            <div class="timeline-header">
                <h3>{deg}</h3>
                <span class="badge">{yr}</span>
            </div>
            <div class="company">{inst}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} — Portfolio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <!-- Navigation -->
  <nav class="navbar">
    <div class="container nav-content">
      <a href="#" class="logo">{name}<span>.</span></a>
      <div class="nav-links">
        <a href="#about">About</a>
        <a href="#skills">Skills</a>
        <a href="#experience">Experience</a>
        <a href="#projects">Projects</a>
        <a href="#contact" class="btn-primary">Contact</a>
      </div>
    </div>
  </nav>

  <!-- Hero Section -->
  <header class="hero">
    <div class="container hero-container">
      <div class="hero-badge">Available for Opportunities</div>
      <h1 class="hero-title">Hi, I'm <span class="highlight">{name}</span></h1>
      <p class="hero-subtitle">{headline}</p>
      <div class="hero-actions">
        <a href="#projects" class="btn btn-primary">View Projects</a>
        <a href="#contact" class="btn btn-outline">Get in Touch</a>
      </div>
    </div>
  </header>

  <!-- About Section -->
  <section id="about" class="section">
    <div class="container">
      <h2 class="section-title">About Me</h2>
      <div class="about-card">
        <p class="about-text">{bio}</p>
        <div class="info-grid">
          <div><strong>Location:</strong> {location or 'Open to Remote'}</div>
          <div><strong>Email:</strong> {email}</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Skills Section -->
  <section id="skills" class="section">
    <div class="container">
      <h2 class="section-title">Technical Skills & Expertise</h2>
      <div class="skills-grid">
        {skills_html if skills_html else '<p>No specific skills listed.</p>'}
      </div>
    </div>
  </section>

  <!-- Experience Section -->
  <section id="experience" class="section">
    <div class="container">
      <h2 class="section-title">Experience & Career</h2>
      <div class="timeline">
        {exp_html if exp_html else '<p class="empty-state">No experience items added.</p>'}
      </div>
    </div>
  </section>

  <!-- Projects Section -->
  <section id="projects" class="section">
    <div class="container">
      <h2 class="section-title">Featured Projects</h2>
      <div class="projects-grid">
        {proj_html if proj_html else '<p class="empty-state">No projects added yet.</p>'}
      </div>
    </div>
  </section>

  <!-- Education Section -->
  <section id="education" class="section">
    <div class="container">
      <h2 class="section-title">Education</h2>
      <div class="timeline">
        {edu_html if edu_html else '<p class="empty-state">No education records added.</p>'}
      </div>
    </div>
  </section>

  <!-- Contact Section -->
  <section id="contact" class="section">
    <div class="container">
      <h2 class="section-title">Let's Connect</h2>
      <div class="contact-card">
        <p>Interested in working together or have a question? Feel free to reach out directly.</p>
        <div class="contact-links">
          {f'<a href="mailto:{email}" class="contact-btn">✉ {email}</a>' if email else ''}
          {f'<a href="{github}" target="_blank" class="contact-btn">GitHub</a>' if github else ''}
          {f'<a href="{linkedin}" target="_blank" class="contact-btn">LinkedIn</a>' if linkedin else ''}
        </div>
      </div>
    </div>
  </section>

  <footer class="footer">
    <div class="container">
      <p>&copy; {name}. Generated with JobHelper AI Portfolio Generator.</p>
    </div>
  </footer>

  <script src="script.js"></script>
</body>
</html>"""


def generate_portfolio_css(theme: str = "dark") -> str:
    if theme == "light":
        bg_body = "#f8fafc"
        bg_card = "#ffffff"
        text_primary = "#0f172a"
        text_muted = "#64748b"
        accent = "#2563eb"
        border = "#e2e8f0"
        card_shadow = "0 4px 12px rgba(0,0,0,0.05)"
    elif theme == "gradient":
        bg_body = "#090d16"
        bg_card = "#131b2e"
        text_primary = "#f1f5f9"
        text_muted = "#94a3b8"
        accent = "#8b5cf6"
        border = "rgba(139, 92, 246, 0.25)"
        card_shadow = "0 8px 24px rgba(139, 92, 246, 0.1)"
    else:  # dark
        bg_body = "#0b0f17"
        bg_card = "#111827"
        text_primary = "#f9fafb"
        text_muted = "#9ca3af"
        accent = "#38bdf8"
        border = "#1f2937"
        card_shadow = "0 4px 16px rgba(0,0,0,0.3)"

    return f"""* {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}

body {{
  font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
  background-color: {bg_body};
  color: {text_primary};
  line-height: 1.6;
}}

.container {{
  max-width: 1040px;
  margin: 0 auto;
  padding: 0 24px;
}}

.navbar {{
  position: sticky;
  top: 0;
  background: {bg_body}ee;
  backdrop-filter: blur(8px);
  border-bottom: 1px solid {border};
  z-index: 100;
  padding: 16px 0;
}}

.nav-content {{
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.logo {{
  font-size: 20px;
  font-weight: 800;
  color: {text_primary};
  text-decoration: none;
}}

.logo span {{
  color: {accent};
}}

.nav-links {{
  display: flex;
  align-items: center;
  gap: 20px;
}}

.nav-links a {{
  color: {text_muted};
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s;
}}

.nav-links a:hover {{
  color: {accent};
}}

.hero {{
  padding: 100px 0 80px;
  text-align: center;
}}

.hero-badge {{
  display: inline-block;
  padding: 6px 14px;
  background: {accent}18;
  color: {accent};
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 20px;
  border: 1px solid {accent}30;
}}

.hero-title {{
  font-size: clamp(32px, 6vw, 56px);
  font-weight: 800;
  letter-spacing: -1px;
  margin-bottom: 16px;
}}

.highlight {{
  color: {accent};
}}

.hero-subtitle {{
  font-size: clamp(16px, 2.5vw, 20px);
  color: {text_muted};
  max-width: 600px;
  margin: 0 auto 32px;
}}

.hero-actions {{
  display: flex;
  justify-content: center;
  gap: 16px;
}}

.btn {{
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  display: inline-block;
}}

.btn-primary {{
  background: {accent};
  color: #fff;
  border: 1px solid {accent};
}}

.btn-primary:hover {{
  opacity: 0.9;
  transform: translateY(-1px);
}}

.btn-outline {{
  background: transparent;
  color: {text_primary};
  border: 1px solid {border};
}}

.btn-outline:hover {{
  border-color: {accent};
  color: {accent};
}}

.section {{
  padding: 60px 0;
}}

.section-title {{
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 32px;
  border-bottom: 2px solid {border};
  padding-bottom: 12px;
}}

.about-card, .contact-card {{
  background: {bg_card};
  border: 1px solid {border};
  padding: 32px;
  border-radius: 12px;
  box-shadow: {card_shadow};
}}

.about-text {{
  font-size: 16px;
  color: {text_muted};
  margin-bottom: 24px;
}}

.info-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  font-size: 14px;
}}

.skills-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}}

.skill-tag {{
  background: {bg_card};
  border: 1px solid {border};
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: {text_primary};
  transition: border-color 0.2s;
}}

.skill-tag:hover {{
  border-color: {accent};
}}

.timeline {{
  display: flex;
  flex-direction: column;
  gap: 20px;
}}

.timeline-item {{
  background: {bg_card};
  border: 1px solid {border};
  padding: 24px;
  border-radius: 10px;
}}

.timeline-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}}

.timeline-header h3 {{
  font-size: 18px;
  font-weight: 600;
}}

.badge {{
  font-size: 12px;
  background: {accent}1a;
  color: {accent};
  padding: 4px 10px;
  border-radius: 6px;
}}

.company {{
  font-size: 14px;
  font-weight: 500;
  color: {accent};
  margin-bottom: 12px;
}}

.timeline-item p {{
  font-size: 14px;
  color: {text_muted};
}}

.projects-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}}

.project-card {{
  background: {bg_card};
  border: 1px solid {border};
  padding: 24px;
  border-radius: 10px;
  transition: transform 0.2s;
}}

.project-card:hover {{
  transform: translateY(-3px);
  border-color: {accent};
}}

.project-header {{
  margin-bottom: 12px;
}}

.project-header h3 {{
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}}

.project-tech {{
  font-size: 12px;
  color: {accent};
  font-weight: 500;
}}

.project-card p {{
  font-size: 14px;
  color: {text_muted};
}}

.contact-links {{
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}}

.contact-btn {{
  background: {bg_card};
  border: 1px solid {border};
  padding: 10px 20px;
  border-radius: 8px;
  color: {text_primary};
  text-decoration: none;
  font-size: 14px;
  transition: border-color 0.2s;
}}

.contact-btn:hover {{
  border-color: {accent};
  color: {accent};
}}

.footer {{
  padding: 40px 0;
  text-align: center;
  border-top: 1px solid {border};
  font-size: 13px;
  color: {text_muted};
}}

@media (max-width: 640px) {{
  .nav-links {{
    display: none;
  }}
  .timeline-header {{
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }}
}}
"""


def generate_portfolio_js() -> str:
    return """// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});
console.log('Portfolio initialized successfully.');
"""


def create_portfolio_zip(data: dict, theme: str = "dark") -> bytes:
    """Builds a ZIP archive containing index.html, style.css, script.js, and README.md."""
    html_content = generate_portfolio_html(data, theme=theme)
    css_content = generate_portfolio_css(theme=theme)
    js_content = generate_portfolio_js()

    name = data.get("full_name") or "User"
    readme_content = f"""# {name} — Personal Portfolio

Generated by **JobHelper AI — AI Resume Analyzer & Career Assistant**.

## How to Deploy Free:
1. **GitHub Pages**:
   - Create a GitHub repository named `username.github.io`
   - Upload these files (`index.html`, `style.css`, `script.js`) to the repository
   - Your portfolio is immediately live!
2. **Netlify or Vercel**:
   - Drag and drop this extracted folder into Netlify Drop (app.netlify.com/drop)
   - Live in 10 seconds with free custom domain support!
"""

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.html", html_content)
        zf.writestr("style.css", css_content)
        zf.writestr("script.js", js_content)
        zf.writestr("README.md", readme_content)

    zip_bytes = zip_buffer.getvalue()
    zip_buffer.close()
    return zip_bytes
