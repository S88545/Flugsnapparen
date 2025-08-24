# =================================================================
# FIL: app/models.py (UPPDATERAD)
# =================================================================
from .extensions import db
from datetime import datetime, date

class TransactionType(db.Model):
    __tablename__ = 'TransactionTypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    transactions = db.relationship('Transaction', backref='type', lazy=True)
    prognoses = db.relationship('Prognosis', backref='type', lazy=True, cascade="all, delete-orphan")

class Transaction(db.Model):
    __tablename__ = 'Transactions'
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type_id = db.Column(db.Integer, db.ForeignKey('TransactionTypes.id'), nullable=False)
    # Legacy fria textfält (behålls för bakåtkompatibilitet)
    supplier = db.Column(db.String(255), nullable=True)
    member = db.Column(db.String(255), nullable=True)
    # Nya relationer till registertabeller (om kolumnerna finns i DB)
    supplier_id = db.Column(db.Integer, db.ForeignKey('Suppliers.id'), nullable=True)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'), nullable=True)
    supplier_ref = db.relationship('Supplier', foreign_keys=[supplier_id], lazy='joined')
    member_ref = db.relationship('Member', foreign_keys=[member_id], lazy='joined')

class YearlySetting(db.Model):
    __tablename__ = 'YearlySettings'
    year = db.Column(db.Integer, primary_key=True)
    total_yta_kvm = db.Column(db.Numeric(10, 2), nullable=False)
    totala_lan = db.Column(db.Numeric(18, 2), nullable=False)
    totala_arsavgifter = db.Column(db.Numeric(18, 2), nullable=False)
    tillgodohavande_placering = db.Column(db.Numeric(18, 2), nullable=False)

# NY MODELL
class Prognosis(db.Model):
    __tablename__ = 'Prognosis'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    transaction_type_id = db.Column(db.Integer, db.ForeignKey('TransactionTypes.id'), nullable=False)
    prognosis_amount = db.Column(db.Numeric(18, 2), nullable=False)

# Register-tabeller för unika namn
class Supplier(db.Model):
    __tablename__ = 'Suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    # backref i Transaction via supplier_ref

class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    # backref i Transaction via member_ref

class Apartment(db.Model):
    __tablename__ = 'Apartments'
    id = db.Column(db.Integer, primary_key=True)
    apartment_number = db.Column(db.String(5), nullable=False, unique=True)
    sqm_area = db.Column(db.Integer, nullable=False)
    share = db.Column(db.Numeric(5, 2), nullable=False)  # 0.00..1.00
    quarterly_charge = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    ownerships = db.relationship(
        'ApartmentOwnership',
        back_populates='apartment',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def current_ownership(self):
        return (self.ownerships
                .filter_by(valid_to=None)
                .order_by(ApartmentOwnership.valid_from.desc())
                .first())

class ApartmentOwnership(db.Model):
    __tablename__ = 'ApartmentOwnerships'
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('Apartments.id'), nullable=False, index=True)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'), nullable=False, index=True)
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    apartment = db.relationship('Apartment', back_populates='ownerships')
    member_ref = db.relationship('Member')