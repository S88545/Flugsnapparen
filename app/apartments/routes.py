from flask import render_template, request, redirect, url_for, flash
from . import apartments
from ..extensions import db
from ..models import Apartment, ApartmentOwnership, Member, YearlySetting
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.exc import IntegrityError


def get_yearly(year: int | None):
    y = year or date.today().year
    ys = YearlySetting.query.get(y)
    if not ys:
        # Fall back to latest available setting
        ys = YearlySetting.query.order_by(YearlySetting.year.desc()).first()
    return ys


@apartments.route('/')
def list():
    items = Apartment.query.order_by(Apartment.apartment_number).all()
    return render_template('apartments/apartment_list.html', items=items)


@apartments.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        apt_no = request.form.get('apartment_number')
        sqm = request.form.get('sqm_area', type=int)
        year = request.form.get('year', type=int)
        if not apt_no or not sqm:
            flash('Lägenhetsnummer och yta krävs.', 'danger')
            return redirect(url_for('apartments.add'))

        # Unik kontroll för lägenhetsnummer
        if Apartment.query.filter_by(apartment_number=apt_no).first():
            flash('Lägenhetsnumret finns redan.', 'danger')
            return redirect(url_for('apartments.add'))

        ys = get_yearly(year)
        if not ys:
            flash('Saknar YearlySettings. Lägg till för aktuellt år först.', 'danger')
            return redirect(url_for('apartments.add'))

        # Korrekt andel: sqm_area / total_yta_kvm (mellan 0 och 1)
        denom = ys.total_yta_kvm if ys.total_yta_kvm and ys.total_yta_kvm > 0 else Decimal(1)
        share = Decimal(sqm) / Decimal(denom)
        # Kvartalsavgift: totala_arsavgifter * share / 4
        quarterly_charge = int(round(float(ys.totala_arsavgifter or 0) * float(share) / 4))

        a = Apartment(
            apartment_number=apt_no,
            sqm_area=sqm,
            share=share,
            quarterly_charge=quarterly_charge,
        )
        db.session.add(a)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Kunde inte spara. Kontrollera att lägenhetsnumret är unikt.', 'danger')
            return redirect(url_for('apartments.add'))
        flash('Lägenhet skapad.', 'success')
        return redirect(url_for('apartments.list'))

    years = [y.year for y in YearlySetting.query.order_by(YearlySetting.year.desc()).all()]
    return render_template('apartments/apartment_form.html', title='Ny lägenhet', years=years)


@apartments.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    a = Apartment.query.get_or_404(id)
    if request.method == 'POST':
        apt_no = request.form.get('apartment_number')
        sqm = request.form.get('sqm_area', type=int)
        year = request.form.get('year', type=int)
        if not apt_no or not sqm:
            flash('Lägenhetsnummer och yta krävs.', 'danger')
            return redirect(url_for('apartments.edit', id=id))

        ys = get_yearly(year)
        if not ys:
            flash('Saknar YearlySettings. Lägg till för aktuellt år först.', 'danger')
            return redirect(url_for('apartments.edit', id=id))

        # Unik kontroll vid ändring
        if Apartment.query.filter(Apartment.apartment_number == apt_no, Apartment.id != id).first():
            flash('Lägenhetsnumret finns redan.', 'danger')
            return redirect(url_for('apartments.edit', id=id))

        a.apartment_number = apt_no
        a.sqm_area = sqm
        denom = ys.total_yta_kvm if ys.total_yta_kvm and ys.total_yta_kvm > 0 else Decimal(1)
        share = Decimal(sqm) / Decimal(denom)
        a.share = share
        a.quarterly_charge = int(round(float(ys.totala_arsavgifter or 0) * float(share) / 4))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Kunde inte uppdatera. Kontrollera att lägenhetsnumret är unikt.', 'danger')
            return redirect(url_for('apartments.edit', id=id))
        flash('Lägenhet uppdaterad.', 'success')
        return redirect(url_for('apartments.list'))

    years = [y.year for y in YearlySetting.query.order_by(YearlySetting.year.desc()).all()]
    return render_template('apartments/apartment_form.html', title='Redigera lägenhet', item=a, years=years)


@apartments.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    a = Apartment.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    flash('Lägenhet borttagen.', 'success')
    return redirect(url_for('apartments.list'))


# Ownerships
@apartments.route('/ownerships/<int:apartment_id>')
def ownerships(apartment_id):
    a = Apartment.query.get_or_404(apartment_id)
    rows = a.ownerships.order_by(ApartmentOwnership.valid_from.desc()).all()
    return render_template('apartments/ownership_list.html', apartment=a, rows=rows)


@apartments.route('/ownerships/<int:apartment_id>/add', methods=['GET', 'POST'])
def ownership_add(apartment_id):
    a = Apartment.query.get_or_404(apartment_id)
    if request.method == 'POST':
        member_id = request.form.get('member_id', type=int)
        valid_from = request.form.get('valid_from')
        if not member_id or not valid_from:
            flash('Medlem och giltig från-datum krävs.', 'danger')
            return redirect(url_for('apartments.ownership_add', apartment_id=apartment_id))

        new_from = datetime.strptime(valid_from, '%Y-%m-%d').date()

        # Validera att det inte finns överlapp
        overlap = (
            ApartmentOwnership.query
            .filter(
                ApartmentOwnership.apartment_id == apartment_id,
                ApartmentOwnership.valid_from <= new_from,
                (ApartmentOwnership.valid_to.is_(None) | (ApartmentOwnership.valid_to >= new_from))
            )
            .first()
        )
        if overlap:
            flash('Datum överlappar befintligt ägande. Avsluta först eller välj ett senare datum.', 'danger')
            return redirect(url_for('apartments.ownership_add', apartment_id=apartment_id))

        # Avsluta nuvarande ägande om det finns (dagen innan nytt startdatum)
        current = a.current_ownership
        if current and current.valid_to is None and current.valid_from < new_from:
            current.valid_to = new_from - timedelta(days=1)

        row = ApartmentOwnership(
            apartment_id=apartment_id,
            member_id=member_id,
            valid_from=new_from,
        )
        db.session.add(row)
        db.session.commit()
        flash('Ägarpost tillagd.', 'success')
        return redirect(url_for('apartments.ownerships', apartment_id=apartment_id))

    members = Member.query.order_by(Member.name).all()
    return render_template('apartments/ownership_form.html', apartment=a, members=members, title='Ny ägare')


@apartments.route('/ownerships/<int:apartment_id>/end', methods=['GET', 'POST'])
def ownership_end(apartment_id):
    a = Apartment.query.get_or_404(apartment_id)
    current = a.current_ownership
    if not current or current.valid_to is not None:
        flash('Det finns inget pågående ägande att avsluta.', 'danger')
        return redirect(url_for('apartments.ownerships', apartment_id=apartment_id))
    if request.method == 'POST':
        end_date = request.form.get('valid_to')
        if not end_date:
            flash('Ange ett slutdatum.', 'danger')
            return redirect(url_for('apartments.ownership_end', apartment_id=apartment_id))
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        if end_date < current.valid_from:
            flash('Slutdatum kan inte vara före startdatum.', 'danger')
            return redirect(url_for('apartments.ownership_end', apartment_id=apartment_id))
        current.valid_to = end_date
        db.session.commit()
        flash('Ägande avslutat.', 'success')
        return redirect(url_for('apartments.ownerships', apartment_id=apartment_id))

    return render_template('apartments/ownership_end_form.html', apartment=a, title='Avsluta aktuellt ägande')


@apartments.route('/ownerships/delete/<int:id>', methods=['POST'])
def ownership_delete(id):
    row = ApartmentOwnership.query.get_or_404(id)
    apartment_id = row.apartment_id
    db.session.delete(row)
    db.session.commit()
    flash('Ägarpost borttagen.', 'success')
    return redirect(url_for('apartments.ownerships', apartment_id=apartment_id))
