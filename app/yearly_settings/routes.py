# =================================================================
# FIL: app/yearly_settings/routes.py
# =================================================================
from flask import render_template, request, redirect, url_for, flash
from . import yearly_settings
from ..models import YearlySetting
from ..extensions import db

@yearly_settings.route('/')
def list():
    all_settings = YearlySetting.query.order_by(YearlySetting.year.desc()).all()
    return render_template('yearly_settings/settings_list.html', all_settings=all_settings)

@yearly_settings.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        year = request.form.get('year')
        if not year or not year.isdigit():
            flash('Ogiltigt år angivet.', 'danger')
            return redirect(url_for('yearly_settings.add'))
        
        existing = YearlySetting.query.get(int(year))
        if existing:
            flash(f'Inställningar för år {year} finns redan.', 'warning')
            return redirect(url_for('yearly_settings.edit', year=year))

        new_settings = YearlySetting(
            year=int(year),
            total_yta_kvm=request.form.get('total_yta_kvm', 0),
            totala_lan=request.form.get('totala_lan', 0),
            totala_arsavgifter=request.form.get('totala_arsavgifter', 0),
            tillgodohavande_placering=request.form.get('tillgodohavande_placering', 0)
        )
        db.session.add(new_settings)
        db.session.commit()
        flash(f'Inställningar för år {year} har sparats.', 'success')
        return redirect(url_for('yearly_settings.list'))
        
    return render_template('yearly_settings/settings_form.html', title="Lägg till Årsinställningar")

@yearly_settings.route('/edit/<int:year>', methods=['GET', 'POST'])
def edit(year):
    settings_to_edit = YearlySetting.query.get_or_404(year)
    if request.method == 'POST':
        settings_to_edit.total_yta_kvm = request.form.get('total_yta_kvm')
        settings_to_edit.totala_lan = request.form.get('totala_lan')
        settings_to_edit.totala_arsavgifter = request.form.get('totala_arsavgifter')
        settings_to_edit.tillgodohavande_placering = request.form.get('tillgodohavande_placering')
        db.session.commit()
        flash(f'Inställningar för år {year} har uppdaterats.', 'success')
        return redirect(url_for('yearly_settings.list'))

    return render_template('yearly_settings/settings_form.html', title=f"Ändra Inställningar för {year}", settings=settings_to_edit)

@yearly_settings.route('/delete/<int:year>', methods=['POST'])
def delete(year):
    settings_to_delete = YearlySetting.query.get_or_404(year)
    db.session.delete(settings_to_delete)
    db.session.commit()
    flash(f'Inställningar för år {year} har tagits bort.', 'success')
    return redirect(url_for('yearly_settings.list'))