# =================================================================
# NY FIL: app/main/__init__.py
#
# BESKRIVNING:
# Initierar vår första "Blueprint". En blueprint är en samling
# routes (URL:er) som hör ihop, t.ex. allt som rör huvudsidorna.
# =================================================================
from flask import Blueprint

main = Blueprint('main', __name__)

# Importerar routes sist för att undvika cirkulära beroenden
from . import routes