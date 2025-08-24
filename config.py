# =================================================================
# FIL: config.py
#
# BESKRIVNING:
# Hanterar konfiguration för applikationen, framförallt
# anslutningssträngen till databasen. (INGEN ÄNDRING HÄR)
# =================================================================
import os

# Basmappen för projektet
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Grundläggande konfigurationsklass.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'en-mycket-hemlig-nyckel'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """
    Konfiguration för utvecklingsmiljön.
    Använder dina databasuppgifter.
    """
    DEBUG = True
    # Anslutningssträng för SQL Server med Trusted Connection (Windows Authentication).
    # Standard: server 'int5_dev' och databas 'Flugsnapparen'.
    # Du kan överskrida via miljövariablerna DB_SERVER och DB_NAME.
    # Standardserver: din angivna named instance
    _DB_SERVER = os.environ.get('DB_SERVER', r'DESKTOP-RKS38AD\SQLEXPRESS')
    _DB_NAME = os.environ.get('DB_NAME', 'Flugsnapparen')
    # Denna sträng säger åt SQLAlchemy att använda pyodbc-drivrutinen.
    SQLALCHEMY_DATABASE_URI = (
        f'mssql+pyodbc://{_DB_SERVER}/{_DB_NAME}'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&Trusted_Connection=yes'
    )

# En dictionary för att enkelt kunna välja konfiguration
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}