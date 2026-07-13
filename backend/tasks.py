from celery import shared_task
from extensions import mail
from flask_mail import Message
from models.drive import PlacementDrive
from models.application import Application
from models.student import StudentProfile
from models.user import User
from datetime import datetime, timedelta
import csv
import io
import time

@shared_task
def send_email_notification(to_email, subject, body, html_body=None, attachment_name=None, attachment_data=None):
    """
    Sends an email using Flask-Mail.
    """
    msg = Message(subject=subject, recipients=[to_email])
    msg.body = body
    if html_body:
        msg.html = html_body
    if attachment_name and attachment_data:
        msg.attach(attachment_name, "text/csv", attachment_data)
        
    try:
        # Since MAIL_SUPPRESS_SEND=True, this will just print in terminal
        # But we format it properly for Flask-Mail
        mail.send(msg)
        print(f"\n[CELERY BACKGROUND TASK] Email successfully sent to {to_email}.")
        print(f"Subject: {subject}")
        print(f"Attachment included: {bool(attachment_name)}\n")
        return f"Email sent to {to_email}"
    except Exception as e:
        print(f"[CELERY BACKGROUND TASK] Failed to send email to {to_email}: {str(e)}")
        return f"Failed to send email to {to_email}"

@shared_task
def send_daily_reminders():
    """
    Scheduled Job: Sends daily reminders to students about upcoming application deadlines.
    Looks for drives closing within the next 3 days.
    """
    now = datetime.utcnow()
    deadline_threshold = now + timedelta(days=3)
    
    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'APPROVED',
        PlacementDrive.application_deadline > now,
        PlacementDrive.application_deadline <= deadline_threshold
    ).all()
    
    if not upcoming_drives:
        return "No upcoming deadlines to remind about."
        
    # Get all active students
    students = StudentProfile.query.all()
    
    count = 0
    for student in students:
        student_user = User.query.get(student.user_id)
        if not student_user: continue
        
        # Check which upcoming drives they haven't applied to
        unapplied = []
        for drive in upcoming_drives:
            has_applied = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
            if not has_applied:
                unapplied.append(drive)
                
        if unapplied:
            drive_names = ", ".join([d.title for d in unapplied])
            body = f"Hello {student.full_name},\n\nThis is a friendly reminder that the deadlines for the following placement drives are approaching within the next 3 days:\n\n{drive_names}\n\nDon't forget to apply!\n\nBest,\nPlacement Cell"
            send_email_notification(student_user.email, "Upcoming Placement Drive Deadlines", body)
            count += 1
            
    return f"Sent reminders to {count} students."

@shared_task
def generate_monthly_report():
    """
    Scheduled Job: Generates monthly placement activity report for the Admin.
    """
    now = datetime.utcnow()
    first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Basic stat calculation for all time, or could be last month
    
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    total_selected = Application.query.filter_by(status='SELECTED').count()
    
    html_body = f"""
    <h2>Monthly Placement Activity Report</h2>
    <p>Report generated on: {now.strftime('%Y-%m-%d')}</p>
    <ul>
        <li><strong>Total Drives Conducted:</strong> {total_drives}</li>
        <li><strong>Total Students Applied:</strong> {total_applications}</li>
        <li><strong>Total Students Selected:</strong> {total_selected}</li>
    </ul>
    <p>Keep up the great work!</p>
    """
    
    send_email_notification('admin@placement.com', "Monthly Placement Activity Report", "Please see HTML version.", html_body=html_body)
    return "Monthly report sent to Admin."

@shared_task
def export_applications_csv(student_id, student_email):
    """
    Async Job: Generates a CSV of a student's applications and emails it to them.
    """
    apps = Application.query.filter_by(student_id=student_id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Applied Date'])
    
    for app in apps:
        writer.writerow([
            app.student_id,
            app.drive.company.company_name,
            app.drive.title,
            app.status,
            app.applied_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    csv_data = output.getvalue()
    
    body = "Your requested placement application history export is attached as a CSV file."
    send_email_notification(student_email, "Your Application History Export", body, attachment_name="application_history.csv", attachment_data=csv_data)
    
    return f"Exported {len(apps)} applications for student {student_id} to CSV."
