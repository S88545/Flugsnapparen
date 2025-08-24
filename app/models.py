# =================================================================
# FIL: app/models.py (UPPDATERAD)
# =================================================================
from .extensions import db

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