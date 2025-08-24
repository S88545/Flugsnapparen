# =================================================================
# FIL: app/prognosis/routes.py (UPPDATERAD)
# =================================================================
from flask import render_template, request, redirect, url_for, flash
from . import prognosis
from ..models import Transaction, TransactionType, Prognosis
from ..extensions import db
from sqlalchemy import func, extract
import datetime
from decimal import Decimal, ROUND_HALF_UP

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
                # Normalisera och kvantisera till 2 decimaler, undvik 0E-10
                if value is None or value == "":
                    amount = Decimal('0.00')
                else:
                    d = Decimal(str(value))
                    if abs(d) < Decimal('0.0000001'):
                        d = Decimal('0')
                    amount = d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                
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

    # Månadstotaler (summa över alla kategorier per månad)
    monthly_totals = {m: Decimal('0.00') for m in range(1, 13)}
    for (type_id, month), amount in prognosis_data.items():
        d = Decimal(str(amount or 0))
        if abs(d) < Decimal('0.0000001'):
            d = Decimal('0')
        monthly_totals[month] = (monthly_totals[month] + d)
    for m in monthly_totals:
        monthly_totals[m] = monthly_totals[m].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    available_years_query = db.session.query(extract('year', Transaction.transaction_date)).distinct().order_by(extract('year', Transaction.transaction_date).desc())
    available_years = [y[0] for y in available_years_query.all()]
    prev_year = max(available_years) if available_years else year - 1

    return render_template('prognosis/prognosis_form.html',
                           categories=categories,
                           prognosis_data=prognosis_data,
                           monthly_totals=monthly_totals,
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
            total = Decimal(str(actual.total or 0))
            total = (Decimal('0') if abs(total) < Decimal('0.0000001') else total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            db.session.add(Prognosis(year=year, month=actual.month, transaction_type_id=actual.transaction_type_id, prognosis_amount=total))

        # 2. Beräkna genomsnitt för innevarande år för framtida månader
        current_year_sums = db.session.query(
            Transaction.transaction_type_id,
            func.sum(Transaction.amount).label('total')
        ).filter(
            extract('year', Transaction.transaction_date) == year,
            extract('month', Transaction.transaction_date) <= current_month
        ).group_by(Transaction.transaction_type_id).all()

        monthly_averages = {}
        for item in current_year_sums:
            total = Decimal(str(item.total or 0))
            avg = (total / Decimal(current_month)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            monthly_averages[item.transaction_type_id] = avg

        all_type_ids = [type.id for type in TransactionType.query.all()]
        for month in range(current_month + 1, 13):
            for type_id in all_type_ids:
                avg_amount = monthly_averages.get(type_id, Decimal('0.00'))
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
            total = Decimal(str(actual.total or 0))
            total = (Decimal('0') if abs(total) < Decimal('0.0000001') else total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            db.session.add(Prognosis(year=year, month=actual.month, transaction_type_id=actual.transaction_type_id, prognosis_amount=total))
        
        flash(f'En linjär prognos för {year} har genererats baserat på utfallet från {from_year}.', 'success')

    db.session.commit()
    return redirect(url_for('prognosis.manage', year=year))