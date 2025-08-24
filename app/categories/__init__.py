# =================================================================
# NY FIL: app/categories/__init__.py
#
# BESKRIVNING:
# Initierar vår nya blueprint för kategorier.
# =================================================================
from flask import Blueprint

categories = Blueprint('categories', __name__)

from . import routes