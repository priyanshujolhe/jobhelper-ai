from flask import Blueprint

builder_bp = Blueprint("builder", __name__, url_prefix="/builder")

from app.resume_builder import routes  # noqa: E402, F401
