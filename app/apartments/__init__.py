from flask import Blueprint

apartments = Blueprint('apartments', __name__)

from . import routes  # noqa: E402,F401
