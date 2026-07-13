from extensions import db
from datetime import datetime

class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    interview_date = db.Column(db.DateTime, nullable=False)
    interview_mode = db.Column(db.String(50)) # e.g., IN-PERSON, VIRTUAL
    meeting_link = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
