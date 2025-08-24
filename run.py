# =================================================================
# FIL: run.py (UPPDATERAD)
#
# BESKRIVNING:
# Denna fil är nu mycket enklare. Dess enda jobb är att skapa
# appen via vår factory-funktion och starta webbservern.
# =================================================================
import os
from app import create_app

# Skapar appen med 'default' (DevelopmentConfig) konfigurationen.
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Detta block körs bara när du exekverar 'python run.py'
if __name__ == '__main__':
    app.run(debug=True)