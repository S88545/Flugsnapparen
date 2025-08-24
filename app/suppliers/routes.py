from flask import render_template, request, redirect, url_for, flash
from . import suppliers
from ..extensions import db
from ..models import Supplier


@suppliers.route('/')
def list():
    items = Supplier.query.order_by(Supplier.name).all()
    return render_template('suppliers/supplier_list.html', items=items)


@suppliers.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Namn är obligatoriskt.', 'danger')
            return redirect(url_for('suppliers.add'))
        db.session.add(Supplier(name=name))
        db.session.commit()
        flash('Leverantör skapad.', 'success')
        return redirect(url_for('suppliers.list'))
    return render_template('suppliers/supplier_form.html', title='Ny leverantör')


@suppliers.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    item = Supplier.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Namn är obligatoriskt.', 'danger')
            return redirect(url_for('suppliers.edit', id=id))
        item.name = name
        db.session.commit()
        flash('Leverantör uppdaterad.', 'success')
        return redirect(url_for('suppliers.list'))
    return render_template('suppliers/supplier_form.html', title='Redigera leverantör', item=item)


@suppliers.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    item = Supplier.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Leverantör borttagen.', 'success')
    return redirect(url_for('suppliers.list'))
