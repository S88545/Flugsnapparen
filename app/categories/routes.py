# =================================================================
# NY FIL: app/categories/routes.py
#
# BESKRIVNING:
# Innehåller all logik för att lista, lägga till, ändra och
# ta bort transaktionstyper (kategorier).
# =================================================================
from flask import render_template, request, redirect, url_for, flash
from . import categories
from ..models import Transaction, TransactionType
from ..extensions import db
from sqlalchemy.exc import IntegrityError

@categories.route('/')
def list():
    """Visar en lista med alla kategorier och ett formulär för att lägga till nya."""
    all_categories = TransactionType.query.order_by(TransactionType.name).all()
    return render_template('categories/category_list.html', categories=all_categories)

@categories.route('/add', methods=['POST'])
def add():
    """Lägger till en ny kategori."""
    name = request.form.get('name')
    if name:
        # Kontrollera om kategorin redan finns
        existing_type = TransactionType.query.filter_by(name=name).first()
        if existing_type:
            flash(f'Kategorin "{name}" finns redan.', 'warning')
        else:
            new_type = TransactionType(name=name)
            db.session.add(new_type)
            db.session.commit()
            flash(f'Kategorin "{name}" har lagts till.', 'success')
    else:
        flash('Kategorinamn får inte vara tomt.', 'danger')
        
    return redirect(url_for('categories.list'))


@categories.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Hanterar redigering av en befintlig kategori."""
    category_to_edit = TransactionType.query.get_or_404(id)

    if request.method == 'POST':
        new_name = request.form.get('name')
        if not new_name:
            flash('Kategorinamn får inte vara tomt.', 'danger')
            return redirect(url_for('categories.edit', id=id))

        # Kontrollera att det nya namnet inte redan används av en annan kategori
        existing_type = TransactionType.query.filter(TransactionType.id != id, TransactionType.name == new_name).first()
        if existing_type:
            flash(f'Kategorinamnet "{new_name}" används redan.', 'warning')
        else:
            category_to_edit.name = new_name
            db.session.commit()
            flash('Kategorin har uppdaterats.', 'success')
            return redirect(url_for('categories.list'))

    return render_template('categories/category_form.html', category=category_to_edit)


@categories.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Tar bort en kategori."""
    category_to_delete = TransactionType.query.get_or_404(id)
    
    # Kontrollera om kategorin används av några transaktioner
    transaction_count = Transaction.query.filter_by(transaction_type_id=id).count()
    
    if transaction_count > 0:
        flash(f'Kan inte ta bort kategorin "{category_to_delete.name}" eftersom den används av {transaction_count} transaktioner.', 'danger')
    else:
        db.session.delete(category_to_delete)
        db.session.commit()
        flash(f'Kategorin "{category_to_delete.name}" har tagits bort.', 'success')
        
    return redirect(url_for('categories.list'))