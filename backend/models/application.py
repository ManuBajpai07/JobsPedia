from extensions import db
from datetime import datetime
from sqlalchemy import UniqueConstraint

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default='APPLIED') # APPLIED, SHORTLISTED, INTERVIEW_SCHEDULED, SELECTED, REJECTED
    remarks = db.Column(db.Text)
    offered_dates = db.Column(db.Text) # Stored as JSON string
    selected_date = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),
    )

    # Relationships
    interview = db.relationship('Interview', backref='application', uselist=False, cascade="all, delete-orphan")
