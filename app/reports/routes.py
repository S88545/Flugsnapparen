# =================================================================
# FIL: app/reports/routes.py (UPPDATERAD)
# =================================================================
from flask import render_template, request, flash
from . import reports
from ..models import Transaction, TransactionType, YearlySetting, Prognosis
from ..extensions import db
from sqlalchemy import func, extract
import datetime

@reports.route('/summary')
def summary():
    # ... (kod för att hämta år och inställningar är oförändrad) ...
    available_years_query = db.session.query(extract('year', Transaction.transaction_date)).distinct().order_by(extract('year', Transaction.transaction_date).desc())
    available_years = [y[0] for y in available_years_query.all()]
    try:
        selected_year = int(request.args.get('year', available_years[0] if available_years else datetime.date.today().year))
    except (ValueError, IndexError):
        selected_year = datetime.date.today().year
    year_settings = YearlySetting.query.get(selected_year)
    if not year_settings:
        flash(f'Grundinställningar saknas för år {selected_year}.', 'warning')
        year_settings = YearlySetting(year=selected_year, total_yta_kvm=1, totala_lan=0, totala_arsavgifter=1, tillgodohavande_placering=0)

    # Hämta finansiell data
    total_income = db.session.query(func.sum(Transaction.amount)).filter(Transaction.amount > 0, extract('year', Transaction.transaction_date) == selected_year).scalar() or 0
    total_expenses = db.session.query(func.sum(Transaction.amount)).filter(Transaction.amount < 0, extract('year', Transaction.transaction_date) == selected_year).scalar() or 0
    net_result = total_income + total_expenses
    energi_kategorier = ['El', 'Värme', 'Vatten o avlopp']
    energikostnad = db.session.query(func.sum(Transaction.amount)).join(TransactionType).filter(TransactionType.name.in_(energi_kategorier), extract('year', Transaction.transaction_date) == selected_year).scalar() or 0
    
    # Beräkna nyckeltal
    nyckeltal = {
        'arsavgift_kvm': float(year_settings.totala_arsavgifter) / float(year_settings.total_yta_kvm),
        'skuldsattning_kvm': float(year_settings.totala_lan) / float(year_settings.total_yta_kvm),
        'sparande_kvm': float(net_result) / float(year_settings.total_yta_kvm),
        'likvida_medel_kvm': float(year_settings.tillgodohavande_placering) / float(year_settings.total_yta_kvm),
        'energikostnad_kvm': abs(float(energikostnad)) / float(year_settings.total_yta_kvm),
        'rantekanslighet': (float(year_settings.totala_lan) * 0.01) / float(year_settings.totala_arsavgifter)
    }

    # Hämta sammanställning per kategori (UTFALL)
    summary_by_type = db.session.query(TransactionType.name, func.sum(Transaction.amount).label('total_actual')).join(TransactionType).filter(extract('year', Transaction.transaction_date) == selected_year).group_by(TransactionType.name).all()
    
    # Hämta sammanställning per kategori (PROGNOS)
    prognosis_by_type = db.session.query(TransactionType.name, func.sum(Prognosis.prognosis_amount).label('total_prognosis')).join(TransactionType).filter(Prognosis.year == selected_year).group_by(TransactionType.name).all()

    # Kombinera utfall och prognos
    report_data = {item.name: {'actual': item.total_actual, 'prognosis': 0} for item in summary_by_type}
    for item in prognosis_by_type:
        if item.name in report_data:
            report_data[item.name]['prognosis'] = item.total_prognosis
        else:
            report_data[item.name] = {'actual': 0, 'prognosis': item.total_prognosis}
    
    # Förbered data för stapeldiagram
    expense_items = sorted([item for item in report_data.items() if item[1]['actual'] < 0 or item[1]['prognosis'] < 0], key=lambda x: x[1]['actual'])
    chart_labels = [item[0] for item in expense_items]
    chart_actuals = [abs(float(item[1]['actual'])) for item in expense_items]
    chart_prognosis = [abs(float(item[1]['prognosis'])) for item in expense_items]
    chart_data_json = {"labels": chart_labels, "actuals": chart_actuals, "prognosis": chart_prognosis}

    return render_template('reports/summary_report.html',
                           selected_year=selected_year,
                           available_years=available_years,
                           total_income=total_income,
                           total_expenses=total_expenses,
                           net_result=net_result,
                           report_data=report_data,
                           chart_data=chart_data_json,
                           nyckeltal=nyckeltal)
