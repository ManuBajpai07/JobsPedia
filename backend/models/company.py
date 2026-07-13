from extensions import db
from datetime import datetime

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact_name = db.Column(db.String(100), nullable=False)
    hr_email = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default='PENDING') # PENDING, APPROVED, REJECTED
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    drives = db.relationship('PlacementDrive', backref='company', lazy=True)
