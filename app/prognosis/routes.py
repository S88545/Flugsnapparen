# =================================================================
# FIL: app/prognosis/routes.py (UPPDATERAD)
# =================================================================
from flask import render_template, request, redirect, url_for, flash
from . import prognosis
from ..models import Transaction, TransactionType, Prognosis
from ..extensions import db
from sqlalchemy import func, extract
import datetime

@prognosis.route('/', methods=['GET'])
def index():
    current_year = datetime.date.today().year
    return redirect(url_for('prognosis.manage', year=current_year))

@prognosis.route('/manage/<int:year>', methods=['GET', 'POST'])
def manage(year):
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('prognosis-'):
                _, type_id, month = key.split('-')
                amount = value if value else 0
                
                existing = Prognosis.query.filter_by(year=year, month=int(month), transaction_type_id=int(type_id)).first()
                if existing:
                    existing.prognosis_amount = amount
                elif float(amount) != 0: # Spara bara om värdet inte är tomt/noll
                    new_prognosis = Prognosis(year=year, month=int(month), transaction_type_id=int(type_id), prognosis_amount=amount)
                    db.session.add(new_prognosis)
        db.session.commit()
        flash(f'Prognos för {year} har sparats.', 'success')
        return redirect(url_for('prognosis.manage', year=year))

    categories = TransactionType.query.order_by(TransactionType.name).all()
    prognosis_data_query = Prognosis.query.filter_by(year=year).all()
    prognosis_data = {(p.transaction_type_id, p.month): p.prognosis_amount for p in prognosis_data_query}
    
    available_years_query = db.session.query(extract('year', Transaction.transaction_date)).distinct().order_by(extract('year', Transaction.transaction_date).desc())
    available_years = [y[0] for y in available_years_query.all()]
    prev_year = max(available_years) if available_years else year - 1

    return render_template('prognosis/prognosis_form.html',
                           categories=categories,
                           prognosis_data=prognosis_data,
                           selected_year=year,
                           prev_year=prev_year)

@prognosis.route('/generate/<int:year>/from/<int:from_year>')
def generate(year, from_year):
    Prognosis.query.filter_by(year=year).delete()
    db.session.commit()

    today = datetime.date.today()
    
    # Om vi genererar för innevarande år, använd hybridlogik
    if year == today.year:
        current_month = today.month
        
        # 1. Hämta utfall från föregående år för passerade månader
        past_months_actuals = db.session.query(
            extract('month', Transaction.transaction_date).label('month'),
            Transaction.transaction_type_id,
            func.sum(Transaction.amount).label('total')
        ).filter(
            extract('year', Transaction.transaction_date) == from_year,
            extract('month', Transaction.transaction_date) <= current_month
        ).group_by(extract('month', Transaction.transaction_date), Transaction.transaction_type_id).all()

        for actual in past_months_actuals:
            db.session.add(Prognosis(year=year, month=actual.month, transaction_type_id=actual.transaction_type_id, prognosis_amount=actual.total))

        # 2. Beräkna genomsnitt för innevarande år för framtida månader
        current_year_sums = db.session.query(
            Transaction.transaction_type_id,
            func.sum(Transaction.amount).label('total')
        ).filter(
            extract('year', Transaction.transaction_date) == year,
            extract('month', Transaction.transaction_date) <= current_month
        ).group_by(Transaction.transaction_type_id).all()

        monthly_averages = {item.transaction_type_id: item.total / current_month for item in current_year_sums}

        all_type_ids = [type.id for type in TransactionType.query.all()]
        for month in range(current_month + 1, 13):
            for type_id in all_type_ids:
                avg_amount = monthly_averages.get(type_id, 0)
                if avg_amount != 0:
                    db.session.add(Prognosis(year=year, month=month, transaction_type_id=type_id, prognosis_amount=avg_amount))
        
        flash(f'Hybridprognos för {year} har genererats.', 'success')

    # Annars, använd enkel linjär prognos
    else:
        previous_year_actuals = db.session.query(
            extract('month', Transaction.transaction_date).label('month'),
            Transaction.transaction_type_id,
            func.sum(Transaction.amount).label('total')
        ).filter(extract('year', Transaction.transaction_date) == from_year).group_by(extract('month', Transaction.transaction_date), Transaction.transaction_type_id).all()

        if not previous_year_actuals:
            flash(f'Ingen data hittades för {from_year} att basera prognosen på.', 'warning')
            return redirect(url_for('prognosis.manage', year=year))

        for actual in previous_year_actuals:
            db.session.add(Prognosis(year=year, month=actual.month, transaction_type_id=actual.transaction_type_id, prognosis_amount=actual.total))
        
        flash(f'En linjär prognos för {year} har genererats baserat på utfallet från {from_year}.', 'success')

    db.session.commit()
    return redirect(url_for('prognosis.manage', year=year))