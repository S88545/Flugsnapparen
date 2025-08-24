# =================================================================
# NY FIL: app/transactions/__init__.py
#
# BESKRIVNING:
# Initierar vår nya blueprint för transaktioner.
# =================================================================
from flask import Blueprint

transactions = Blueprint('transactions', __name__)

from . import routes