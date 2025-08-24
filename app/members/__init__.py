from flask import Blueprint

members = Blueprint('members', __name__)

from . import routes  # noqa: E402,F401
