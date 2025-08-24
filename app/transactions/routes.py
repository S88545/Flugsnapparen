# =================================================================
# FIL: app/transactions/routes.py (UPPDATERAD)
#
# BESKRIVNING:
# Funktionen 'list' har byggts om för att hantera dynamisk sortering.
# =================================================================
from flask import render_template, request, redirect, url_for, flash
from . import transactions
from ..models import Transaction, TransactionType, Member, Supplier
from ..extensions import db
from datetime import datetime
from sqlalchemy import asc, desc, and_, or_, func
from datetime import date, timedelta

@transactions.route('/')
def list():
    """Visar en lista med alla transaktioner, med sorteringsmöjlighet."""
    # Hämta sorteringsparametrar och filter från URL:en
    # Använd 'date' som standard för att matcha sort_columns-nycklar
    sort_by = request.args.get('sort_by', 'date')
    order = request.args.get('order', 'desc')

    preset = request.args.get('preset', 'this_year')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    q = request.args.get('q', '').strip()
    type_id = request.args.get('type_id', type=int)
    member_id = request.args.get('member_id', type=int)
    supplier_id = request.args.get('supplier_id', type=int)
    tag_kind = request.args.get('tag_kind', 'all')  # all|member|supplier|none|any
    amount_min = request.args.get('amount_min', type=float)
    amount_max = request.args.get('amount_max', type=float)

    # Bygg upp grundfrågan mot databasen
    query = Transaction.query

    # Datumintervall
    today = date.today()
    start_date = None
    end_date = None
    if preset and preset != 'custom':
        if preset == 'this_month':
            start_date = today.replace(day=1)
            # nästa månad första dag - 1 dag
            next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_date = next_month - timedelta(days=1)
        elif preset == 'last_month':
            first_this = today.replace(day=1)
            last_month_end = first_this - timedelta(days=1)
            start_date = last_month_end.replace(day=1)
            end_date = last_month_end
        elif preset == 'this_year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        elif preset == 'last_year':
            start_date = today.replace(year=today.year-1, month=1, day=1)
            end_date = today.replace(year=today.year-1, month=12, day=31)
        elif preset == 'last_30':
            start_date = today - timedelta(days=30)
            end_date = today
        elif preset == 'last_90':
            start_date = today - timedelta(days=90)
            end_date = today
        elif preset == 'all':
            start_date = None
            end_date = None
    else:
        # custom
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except Exception:
                start_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except Exception:
                end_date = None
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    # Textsökning (beskrivning)
    if q:
        query = query.filter(func.lower(Transaction.description).like(f"%{q.lower()}%"))

    # Typfilter
    if type_id:
        query = query.filter(Transaction.transaction_type_id == type_id)

    # Taggfilter
    if member_id:
        query = query.filter(Transaction.member_id == member_id)
    if supplier_id:
        query = query.filter(Transaction.supplier_id == supplier_id)
    if tag_kind == 'member':
        query = query.filter(Transaction.member_id.isnot(None), Transaction.supplier_id.is_(None))
    elif tag_kind == 'supplier':
        query = query.filter(Transaction.supplier_id.isnot(None), Transaction.member_id.is_(None))
    elif tag_kind == 'none':
        query = query.filter(Transaction.member_id.is_(None), Transaction.supplier_id.is_(None))
    elif tag_kind == 'any':
        query = query.filter(or_(Transaction.member_id.isnot(None), Transaction.supplier_id.isnot(None)))

    # Beloppsintervall
    if amount_min is not None:
        query = query.filter(Transaction.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(Transaction.amount <= amount_max)

    # Mappa strängar till faktiska databaskolumner
    sort_columns = {
        'date': Transaction.transaction_date,
        'description': Transaction.description,
        'amount': Transaction.amount,
        'type': TransactionType.name
    }

    # Om vi sorterar på typnamn, måste vi koppla ihop tabellerna
    if sort_by == 'type':
        query = query.join(TransactionType)

    # Hämta rätt kolumn att sortera på, med 'datum' som standard
    sort_column = sort_columns.get(sort_by, Transaction.transaction_date)

    # Bygg ORDER BY-klasuler utan duplicering; lägg sekundär sortering på datum om primär ej är datum
    order_clauses = []
    order_clauses.append(desc(sort_column) if order == 'desc' else asc(sort_column))
    if sort_by not in ('date', 'transaction_date'):
        order_clauses.append(desc(Transaction.transaction_date) if order == 'desc' else asc(Transaction.transaction_date))
    query = query.order_by(*order_clauses)
    
    # Beräkna saldo för urvalet (ta bort eventuell ORDER BY för att undvika SQL Server-fel)
    total_balance = (
        query
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .order_by(None)
        .scalar()
    )

    # Hämta poster med redan applicerad sortering
    all_transactions = query.all()

    transaction_types = TransactionType.query.order_by(TransactionType.name).all()
    members = Member.query.order_by(Member.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()

    # Exportera CSV om efterfrågat
    if request.args.get('export') == '1':
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(['Datum', 'Beskrivning', 'Typ', 'Belopp', 'Medlem', 'Leverantör'])
        for tx in all_transactions:
            writer.writerow([
                tx.transaction_date.strftime('%Y-%m-%d'),
                tx.description or '',
                tx.type.name if tx.type else '',
                f"{tx.amount}",
                tx.member_ref.name if getattr(tx, 'member_ref', None) else '',
                tx.supplier_ref.name if getattr(tx, 'supplier_ref', None) else ''
            ])
        csv_data = output.getvalue()
        output.close()
        # Lägg till BOM för Excel-kompat
        bom = '\ufeff'
        from flask import Response
        return Response(bom + csv_data, mimetype='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename=transaktioner.csv'})

    return render_template(
        'transactions/transaction_list.html',
        transactions=all_transactions,
        sort_by=sort_by,
        order=order,
        total_balance=total_balance,
        preset=preset,
        start_date=start_date_str or (start_date.strftime('%Y-%m-%d') if start_date else ''),
        end_date=end_date_str or (end_date.strftime('%Y-%m-%d') if end_date else ''),
        q=q,
        type_id=type_id,
        member_id=member_id,
        supplier_id=supplier_id,
        tag_kind=tag_kind,
        amount_min=amount_min,
        amount_max=amount_max,
        transaction_types=transaction_types,
        members=members,
        suppliers=suppliers,
    )


@transactions.route('/add', methods=['GET', 'POST'])
def add():
    """Hanterar både visning av formulär och skapande av ny transaktion."""
    if request.method == 'POST':
        date_str = request.form.get('transaction_date')
        description = request.form.get('description')
        amount = request.form.get('amount')
        type_id = request.form.get('transaction_type_id')
        member_id = request.form.get('member_id', type=int)
        supplier_id = request.form.get('supplier_id', type=int)

        if not date_str or not amount or not type_id:
            flash('Datum, belopp och typ är obligatoriska fält.', 'danger')
            return redirect(url_for('transactions.add'))

        # Tillåt endast en märkning (antingen medlem eller leverantör)
        if member_id and supplier_id:
            flash('Välj antingen Medlem eller Leverantör, inte båda.', 'danger')
            return redirect(url_for('transactions.add'))

        new_transaction = Transaction(
            transaction_date=datetime.strptime(date_str, '%Y-%m-%d').date(),
            description=description,
            amount=amount,
            transaction_type_id=type_id
        )
        if member_id:
            new_transaction.member_id = member_id
            new_transaction.supplier_id = None
        elif supplier_id:
            new_transaction.supplier_id = supplier_id
            new_transaction.member_id = None
        db.session.add(new_transaction)
        db.session.commit()
        flash('Transaktionen har lagts till.', 'success')
        return redirect(url_for('transactions.list'))

    transaction_types = TransactionType.query.order_by(TransactionType.name).all()
    members = Member.query.order_by(Member.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('transactions/transaction_form.html',
                           title='Lägg till Transaktion',
                           transaction_types=transaction_types,
                           members=members,
                           suppliers=suppliers)


@transactions.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Hanterar redigering av en befintlig transaktion."""
    transaction_to_edit = Transaction.query.get_or_404(id)

    if request.method == 'POST':
        transaction_to_edit.transaction_date = datetime.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date()
        transaction_to_edit.description = request.form.get('description')
        transaction_to_edit.amount = request.form.get('amount')
        transaction_to_edit.transaction_type_id = request.form.get('transaction_type_id')
        member_id = request.form.get('member_id', type=int)
        supplier_id = request.form.get('supplier_id', type=int)

        if member_id and supplier_id:
            flash('Välj antingen Medlem eller Leverantör, inte båda.', 'danger')
            return redirect(url_for('transactions.edit', id=id))

        transaction_to_edit.member_id = member_id if member_id else None
        transaction_to_edit.supplier_id = supplier_id if supplier_id else None
        
        db.session.commit()
        flash('Transaktionen har uppdaterats.', 'success')
        return redirect(url_for('transactions.list'))

    transaction_types = TransactionType.query.order_by(TransactionType.name).all()
    members = Member.query.order_by(Member.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('transactions/transaction_form.html',
                           title='Ändra Transaktion',
                           transaction=transaction_to_edit,
                           transaction_types=transaction_types,
                           members=members,
                           suppliers=suppliers)


@transactions.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Tar bort en transaktion."""
    transaction_to_delete = Transaction.query.get_or_404(id)
    db.session.delete(transaction_to_delete)
    db.session.commit()
    flash('Transaktionen har tagits bort.', 'success')
    return redirect(url_for('transactions.list'))