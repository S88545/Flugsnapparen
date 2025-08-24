# =================================================================
# FIL: app/__init__.py (UPPDATERAD)
# =================================================================
from flask import Flask
from config import config
from .extensions import db

def create_app(config_name):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(config[config_name])
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .transactions import transactions as transactions_blueprint
    app.register_blueprint(transactions_blueprint, url_prefix='/transactions')
    from .reports import reports as reports_blueprint
    app.register_blueprint(reports_blueprint, url_prefix='/reports')
    from .categories import categories as categories_blueprint
    app.register_blueprint(categories_blueprint, url_prefix='/categories')
    from .yearly_settings import yearly_settings as yearly_settings_blueprint
    app.register_blueprint(yearly_settings_blueprint, url_prefix='/yearly-settings')

    # NYTT: Registrera 'prognosis'-blueprinten
    from .prognosis import prognosis as prognosis_blueprint
    app.register_blueprint(prognosis_blueprint, url_prefix='/prognosis')

    @app.context_processor
    def inject_utility_functions():
        def format_currency(value):
            if value is None: value = 0
            value = float(value)
            return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " kr"
        return dict(format_currency=format_currency)

    return app