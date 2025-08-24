# =================================================================
# FIL: app/yearly_settings/__init__.py (KORRIGERAD)
# =================================================================
from flask import Blueprint

yearly_settings = Blueprint('yearly_settings', __name__)

# Denna import MÅSTE vara sist för att undvika cirkulär import.
from . import routes