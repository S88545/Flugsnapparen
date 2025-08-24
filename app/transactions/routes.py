# =================================================================
# FIL: app/transactions/routes.py (UPPDATERAD)
#
# BESKRIVNING:
# Funktionen 'list' har byggts om för att hantera dynamisk sortering.
# =================================================================
from flask import render_template, request, redirect, url_for, flash
from . import transactions
from ..models import Transaction, TransactionType
from ..extensions import db
from datetime import datetime
from sqlalchemy import asc, desc

@transactions.route('/')
def list():
    """Visar en lista med alla transaktioner, med sorteringsmöjlighet."""
    # Hämta sorteringsparametrar från URL:en
    sort_by = request.args.get('sort_by', 'transaction_date')
    order = request.args.get('order', 'desc')

    # Bygg upp grundfrågan mot databasen
    query = Transaction.query

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

    # Applicera sorteringsordningen (stigande eller fallande)
    if order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    all_transactions = query.all()

    return render_template('transactions/transaction_list.html',
                           transactions=all_transactions,
                           sort_by=sort_by,
                           order=order)


@transactions.route('/add', methods=['GET', 'POST'])
def add():
    """Hanterar både visning av formulär och skapande av ny transaktion."""
    if request.method == 'POST':
        date_str = request.form.get('transaction_date')
        description = request.form.get('description')
        amount = request.form.get('amount')
        type_id = request.form.get('transaction_type_id')

        if not date_str or not amount or not type_id:
            flash('Datum, belopp och typ är obligatoriska fält.', 'danger')
            return redirect(url_for('transactions.add'))

        new_transaction = Transaction(
            transaction_date=datetime.strptime(date_str, '%Y-%m-%d').date(),
            description=description,
            amount=amount,
            transaction_type_id=type_id
        )
        db.session.add(new_transaction)
        db.session.commit()
        flash('Transaktionen har lagts till.', 'success')
        return redirect(url_for('transactions.list'))

    transaction_types = TransactionType.query.order_by(TransactionType.name).all()
    return render_template('transactions/transaction_form.html',
                           title='Lägg till Transaktion',
                           transaction_types=transaction_types)


@transactions.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Hanterar redigering av en befintlig transaktion."""
    transaction_to_edit = Transaction.query.get_or_404(id)

    if request.method == 'POST':
        transaction_to_edit.transaction_date = datetime.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date()
        transaction_to_edit.description = request.form.get('description')
        transaction_to_edit.amount = request.form.get('amount')
        transaction_to_edit.transaction_type_id = request.form.get('transaction_type_id')
        
        db.session.commit()
        flash('Transaktionen har uppdaterats.', 'success')
        return redirect(url_for('transactions.list'))

    transaction_types = TransactionType.query.order_by(TransactionType.name).all()
    return render_template('transactions/transaction_form.html',
                           title='Ändra Transaktion',
                           transaction=transaction_to_edit,
                           transaction_types=transaction_types)


@transactions.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Tar bort en transaktion."""
    transaction_to_delete = Transaction.query.get_or_404(id)
    db.session.delete(transaction_to_delete)
    db.session.commit()
    flash('Transaktionen har tagits bort.', 'success')
    return redirect(url_for('transactions.list'))