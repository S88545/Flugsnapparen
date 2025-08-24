# =================================================================
# FIL: app/prognosis/__init__.py (KORRIGERAD)
# =================================================================
from flask import Blueprint

prognosis = Blueprint('prognosis', __name__)

# Denna import MÅSTE vara sist för att undvika cirkulär import.
from . import routes