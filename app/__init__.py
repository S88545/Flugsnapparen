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

    # Nya register: members, suppliers, apartments
    from .members import members as members_blueprint
    app.register_blueprint(members_blueprint, url_prefix='/members')
    from .suppliers import suppliers as suppliers_blueprint
    app.register_blueprint(suppliers_blueprint, url_prefix='/suppliers')
    from .apartments import apartments as apartments_blueprint
    app.register_blueprint(apartments_blueprint, url_prefix='/apartments')

    @app.context_processor
    def inject_utility_functions():
        def format_currency(value):
            if value is None: value = 0
            value = float(value)
            return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " kr"
        # Formattera tal till exakt två decimaler för input-fält (utan valutasymbol)
        def format_number2(value):
            if value is None or value == "":
                return ""
            try:
                from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
                d = Decimal(str(value))
                # Behandla extremt små värden som 0
                if abs(d) < Decimal("0.0000001"):
                    d = Decimal("0")
                d = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                # Använd punkt som decimaltecken för HTML number inputs
                return format(d, 'f')
            except Exception:
                try:
                    return f"{float(value):.2f}"
                except Exception:
                    return ""
        def format_percent(value, decimals: int = 1):
            try:
                if value is None:
                    return "–"
                v = float(value) * 100.0
                fmt = f"{v:.{decimals}f}%"
                return fmt
            except Exception:
                return "–"
        return dict(format_currency=format_currency, format_number2=format_number2, format_percent=format_percent)

    return app