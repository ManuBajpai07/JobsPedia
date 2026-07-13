from extensions import db
from datetime import datetime

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    branch_eligibility = db.Column(db.String(200), nullable=False) # e.g., "CS,IT"
    minimum_cgpa = db.Column(db.Float, nullable=False)
    eligible_year = db.Column(db.Integer, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    package_details = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='PENDING') # PENDING, APPROVED, REJECTED, CLOSED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='drive', lazy=True)
