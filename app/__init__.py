import os
from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import config_by_name
from app.extensions import db, login_manager, csrf


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.resume import resume_bp
    from app.jobs import jobs_bp
    from app.resume_builder import builder_bp
    from app.portfolio import portfolio_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(builder_bp)
    app.register_blueprint(portfolio_bp)

    # Root route: landing page
    @app.route("/")
    def index():
        from app.models import Job
        featured_jobs = Job.query.limit(4).all()
        return render_template("landing.html", featured_jobs=featured_jobs)

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    # Context processors
    @app.context_processor
    def inject_global_data():
        return {
            "app_name": "JobHelper",
            "app_tagline": "AI Resume Analyzer & Job Matcher",
        }

    # Ensure tables and sample data exist
    with app.app_context():
        # Ensure uploads and data directories exist
        os.makedirs(app.config.get("UPLOAD_FOLDER", "app/static/uploads"), exist_ok=True)
        db.create_all()
        from app.jobs.sample_jobs import seed_sample_jobs
        try:
            seed_sample_jobs()
        except Exception:
            pass

    return app
