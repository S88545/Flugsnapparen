# =================================================================
# NY FIL: app/extensions.py
#
# BESKRIVNING:
# Denna fil initierar tillägg (extensions) som används i flera
# delar av appen. Detta förhindrar cirkulära importer.
# =================================================================
from flask_sqlalchemy import SQLAlchemy

# Skapa ett SQLAlchemy-objekt. Detta kommer vi använda för att
# interagera med databasen i resten av appen.
db = SQLAlchemy()