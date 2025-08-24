# =================================================================
# FIL: app/reports/routes.py (UPPDATERAD)
# =================================================================
from flask import render_template, request, flash
from . import reports
from ..models import Transaction, TransactionType, YearlySetting, Prognosis, Apartment, ApartmentOwnership, Member
from ..extensions import db
from sqlalchemy import func, extract, or_
import datetime
from decimal import Decimal

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


@reports.route('/apartment-member')
def apartment_member_report():
    # Årsval baserat på transaktioner, fallback = innevarande år
    available_years_query = db.session.query(extract('year', Transaction.transaction_date)).distinct().order_by(extract('year', Transaction.transaction_date).desc())
    available_years = [y[0] for y in available_years_query.all()]
    try:
        selected_year = int(request.args.get('year', available_years[0] if available_years else datetime.date.today().year))
    except (ValueError, IndexError):
        selected_year = datetime.date.today().year

    start_date = datetime.date(selected_year, 1, 1)
    end_date = datetime.date(selected_year, 12, 31)

    # Hämta äganden som överlappar året (kan bli flera rader per lgh vid ägarbyte)
    ownerships = (
        db.session.query(ApartmentOwnership, Apartment, Member)
        .join(Apartment, ApartmentOwnership.apartment_id == Apartment.id)
        .join(Member, ApartmentOwnership.member_id == Member.id)
        .filter(
            ApartmentOwnership.valid_from <= end_date,
            func.coalesce(ApartmentOwnership.valid_to, end_date) >= start_date,
        )
        .order_by(Apartment.apartment_number, Member.name)
        .all()
    )

    rows = []
    totals = {"paid": Decimal('0.00'), "annual_fee": Decimal('0.00'), "expected": Decimal('0.00'), "delta_annual": Decimal('0.00'), "delta_expected": Decimal('0.00')}
    due_dates = [
        datetime.date(selected_year, 1, 1),
        datetime.date(selected_year, 4, 1),
        datetime.date(selected_year, 7, 1),
        datetime.date(selected_year, 10, 1),
    ]
    today = datetime.date.today()
    if selected_year < today.year:
        cutoff_date = end_date  # hela året
    elif selected_year > today.year:
        cutoff_date = start_date - datetime.timedelta(days=1)  # ingen förväntan ännu
    else:
        cutoff_date = min(today, end_date)
    for own, apt, mem in ownerships:
        overlap_start = max(own.valid_from, start_date)
        overlap_end = min(own.valid_to or end_date, end_date)

        # Betalningar för medlem under ägarperioden
        paid_sum = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.member_id == mem.id,
            Transaction.amount > 0,
            Transaction.transaction_date >= overlap_start,
            Transaction.transaction_date <= overlap_end,
        ).scalar() or 0
        paid = Decimal(str(paid_sum))

        # Årsavgift (kvartalsavgift x4)
        annual_fee = Decimal(str(apt.quarterly_charge or 0)) * Decimal('4')

        # Förväntat: antal förfallodatum upp till cutoff som ligger inom ägarperioden
        expected_count = sum(1 for d in due_dates if overlap_start <= d <= overlap_end and d <= cutoff_date)
        expected = Decimal(str(apt.quarterly_charge or 0)) * Decimal(expected_count)

        delta_annual = paid - annual_fee
        delta_expected = paid - expected

        rows.append({
            "apartment": apt.apartment_number,
            "member": mem.name,
            "paid": paid,
            "annual_fee": annual_fee,
            "expected": expected,
            "delta_annual": delta_annual,
            "delta_expected": delta_expected,
        })
        totals["paid"] += paid
        totals["annual_fee"] += annual_fee
        totals["expected"] += expected
        totals["delta_annual"] += delta_annual
        totals["delta_expected"] += delta_expected

    return render_template(
        'reports/apartment_member_report.html',
        rows=rows,
        totals=totals,
        selected_year=selected_year,
        available_years=available_years,
    )


@reports.route('/kpi')
def kpi_report():
    # Årsval
    available_years_query = db.session.query(extract('year', Transaction.transaction_date)).distinct().order_by(extract('year', Transaction.transaction_date).desc())
    available_years = [y[0] for y in available_years_query.all()]
    try:
        selected_year = int(request.args.get('year', available_years[0] if available_years else datetime.date.today().year))
    except (ValueError, IndexError):
        selected_year = datetime.date.today().year

    ys = YearlySetting.query.get(selected_year)
    if not ys:
        flash(f'Grundinställningar saknas för år {selected_year}.', 'warning')
        ys = YearlySetting(year=selected_year, total_yta_kvm=0, totala_lan=0, totala_arsavgifter=0, tillgodohavande_placering=0)

    total_area = float(ys.total_yta_kvm or 0)
    total_loans = float(ys.totala_lan or 0)
    total_annual_fees = float(ys.totala_arsavgifter or 0)
    savings_balance = float(ys.tillgodohavande_placering or 0)

    # Energi (Värme + Elektricitet) för året (positiv belopp? vi tar absolutbelopp av summan)
    energy_names = ['Värme', 'Elektricitet']
    energy_sum = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).join(TransactionType).filter(
        TransactionType.name.in_(energy_names),
        extract('year', Transaction.transaction_date) == selected_year,
    ).scalar() or 0.0
    energy_cost = abs(float(energy_sum))

    # Inkomster: Bank, ränta, m.m + Medlemsavgifter (positiva belopp)
    revenue_names = ['Bank, ränta, m.m', 'Bank, ränta, m.m.', 'Medlemsavgifter']
    total_revenue = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).join(TransactionType).filter(
        Transaction.amount > 0,
        or_(TransactionType.name.in_(revenue_names), Transaction.transaction_type_id == 6),
        extract('year', Transaction.transaction_date) == selected_year,
    ).scalar() or 0.0
    annual_fees_income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).join(TransactionType).filter(
        Transaction.amount > 0,
        TransactionType.name == 'Medlemsavgifter',
        extract('year', Transaction.transaction_date) == selected_year,
    ).scalar() or 0.0

    # Nyckeltal
    skuld_per_kvm = (total_loans / total_area) if total_area > 0 else None
    sparande_per_kvm = (savings_balance / total_area) if total_area > 0 else None
    rantekanslighet_formell = ((total_loans * 0.01) / total_annual_fees) if total_annual_fees > 0 else None
    # Skala förenklad variant till per 1 %-enhets höjning (matchar formell)
    rantekanslighet_forenklad = ((total_loans / total_annual_fees) * 0.01) if total_annual_fees > 0 else None
    energi_per_kvm = (energy_cost / total_area) if total_area > 0 else None
    arsavgift_per_kvm = (total_annual_fees / total_area) if total_area > 0 else None
    arsavgifter_andel_rorelseintakter = (annual_fees_income / total_revenue) if total_revenue > 0 else None

    # Klassificera räntekänslighet enligt HSB
    def classify_rante(value_ratio):
        if value_ratio is None:
            return ('Okänd', 'text-gray-500')
        pct = value_ratio * 100.0
        if pct <= 5:
            return ('Låg', 'text-green-700')
        if pct <= 9:
            return ('Normal', 'text-amber-600')
        if pct <= 15:
            return ('Hög', 'text-orange-600')
        return ('Mycket hög', 'text-red-700')

    rk_label, rk_class = classify_rante(rantekanslighet_formell)

    metrics = {
        'skuld_per_kvm': skuld_per_kvm,
        'sparande_per_kvm': sparande_per_kvm,
        'rantekanslighet_formell': rantekanslighet_formell,
        'rantekanslighet_forenklad': rantekanslighet_forenklad,
        'energi_per_kvm': energi_per_kvm,
        'arsavgift_per_kvm': arsavgift_per_kvm,
        'arsavgifter_andel_rorelseintakter': arsavgifter_andel_rorelseintakter,
        'rk_label': rk_label,
        'rk_class': rk_class,
    }

    return render_template(
        'reports/kpi_report.html',
        selected_year=selected_year,
        available_years=available_years,
        metrics=metrics,
    )
