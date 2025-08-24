from flask import render_template, request, redirect, url_for, flash
from . import members
from ..extensions import db
from ..models import Member


@members.route('/')
def list():
    items = Member.query.order_by(Member.name).all()
    return render_template('members/member_list.html', items=items)


@members.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Namn är obligatoriskt.', 'danger')
            return redirect(url_for('members.add'))
        db.session.add(Member(name=name))
        db.session.commit()
        flash('Medlem skapad.', 'success')
        return redirect(url_for('members.list'))
    return render_template('members/member_form.html', title='Ny medlem')


@members.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    item = Member.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Namn är obligatoriskt.', 'danger')
            return redirect(url_for('members.edit', id=id))
        item.name = name
        db.session.commit()
        flash('Medlem uppdaterad.', 'success')
        return redirect(url_for('members.list'))
    return render_template('members/member_form.html', title='Redigera medlem', item=item)


@members.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    item = Member.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Medlem borttagen.', 'success')
    return redirect(url_for('members.list'))
