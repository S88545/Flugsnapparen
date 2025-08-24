# =================================================================
# NY FIL: app/reports/__init__.py
#
# BESKRIVNING:
# Initierar vår nya blueprint för rapporter.
# =================================================================
from flask import Blueprint

reports = Blueprint('reports', __name__)

from . import routes