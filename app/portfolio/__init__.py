from flask import Blueprint

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/portfolio")

from app.portfolio import routes  # noqa: E402, F401
