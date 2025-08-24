# =================================================================
# FIL: app/main/routes.py (UPPDATERAD)
#
# BESKRIVNING:
# Denna fil innehåller nu logiken för att hämta all data
# från databasen och skicka den till HTML-mallen.
# =================================================================
from flask import render_template, jsonify
from . import main
from ..models import Transaction, TransactionType
from ..extensions import db
from sqlalchemy import func
import datetime
import json

def format_currency(value):
    """Hjälpfunktion för att formatera tal som svensk valuta."""
    if value is None:
        value = 0
    # Konvertera till float för formatering, om det är Decimal
    value = float(value)
    # Formatterar till "1 234,56 kr"
    return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " kr"

@main.app_context_processor
def inject_utility_functions():
    """
    Gör hjälpfunktioner tillgängliga för alla Jinja2-mallar.
    Detta löser 'UndefinedError' för format_currency.
    """
    return dict(format_currency=format_currency)

@main.route('/')
def index():
    """
    View-funktionen för huvudsidan.
    Hämtar nu data från databasen.
    """
    current_year = datetime.date.today().year

    # 1. Beräkna nyckeltal
    total_balance = db.session.query(func.sum(Transaction.amount)).scalar()
    
    income_this_year = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.amount > 0,
        func.extract('year', Transaction.transaction_date) == current_year
    ).scalar()

    expenses_this_year = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.amount < 0,
        func.extract('year', Transaction.transaction_date) == current_year
    ).scalar()
    
    # Hantera om någon av summorna är None (t.ex. inga utgifter än)
    income_this_year = income_this_year or 0
    expenses_this_year = expenses_this_year or 0
    result_this_year = income_this_year + expenses_this_year

    # 2. Hämta senaste 5 transaktionerna
    latest_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(5).all()

    # 3. Hämta data för kostnadsdiagrammet (utgifter i år per kategori)
    expense_summary = db.session.query(
        TransactionType.name,
        func.sum(Transaction.amount)
    ).join(TransactionType).filter(
        Transaction.amount < 0,
        func.extract('year', Transaction.transaction_date) == current_year
    ).group_by(TransactionType.name).order_by(func.sum(Transaction.amount).asc()).all()

    # Formattera diagramdatan för Chart.js
    chart_labels = [item[0] for item in expense_summary]
    # Använd absoluta värden för diagrammet (inga negativa staplar)
    chart_data = [abs(float(item[1])) for item in expense_summary]

    chart_data_json = {
        "labels": chart_labels,
        "data": chart_data
    }

    # Skicka all data till mallen
    return render_template('index.html',
                           total_balance=format_currency(total_balance),
                           income_this_year=format_currency(income_this_year),
                           expenses_this_year=format_currency(expenses_this_year),
                           result_this_year=format_currency(result_this_year),
                           latest_transactions=latest_transactions,
                           chart_data=chart_data_json)