from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.student import StudentProfile
from models.drive import PlacementDrive
from models.application import Application
from extensions import db, cache
from datetime import datetime

student_bp = Blueprint('student', __name__)

def get_student():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'STUDENT':
        return None
    student = StudentProfile.query.filter_by(user_id=user_id).first()
    return student

@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    student = get_student()
    if not student: return jsonify({"message": "Forbidden"}), 403
    
    total_applied = Application.query.filter_by(student_id=student.id).count()
    shortlisted = Application.query.filter_by(student_id=student.id, status='SHORTLISTED').count()
    selected = Application.query.filter_by(student_id=student.id, status='SELECTED').count()

    stats = {
        "total_applied": total_applied,
        "shortlisted": shortlisted,
        "selected": selected
    }
    return jsonify(stats), 200

@student_bp.route('/drives', methods=['GET'])
@jwt_required()
def get_eligible_drives():
    student = get_student()
    if not student: return jsonify({"message": "Forbidden"}), 403
    
    # Get all APPROVED drives
    drives = PlacementDrive.query.filter_by(status='APPROVED').all()
    res = []
    for d in drives:
        # Check eligibility and if already applied
        applied = Application.query.filter_by(student_id=student.id, drive_id=d.id).first() is not None
        
        # Simple eligibility logic based on branch, CGPA, and year
        # In a real system, you'd parse branch strings, etc.
        is_eligible = True
        if d.minimum_cgpa and student.cgpa < d.minimum_cgpa: is_eligible = False
        if d.eligible_year and student.year > d.eligible_year: is_eligible = False
        if d.branch_eligibility and student.branch not in d.branch_eligibility: is_eligible = False

        res.append({
            "id": d.id,
            "company": d.company.company_name,
            "title": d.title,
            "description": d.job_description,
            "deadline": d.application_deadline,
            "location": d.location,
            "package": d.package_details,
            "is_eligible": is_eligible,
            "applied": applied
        })
        
    return jsonify(res), 200

@student_bp.route('/drives/<int:id>/apply', methods=['POST'])
@jwt_required()
def apply_to_drive(id):
    student = get_student()
    if not student: return jsonify({"message": "Forbidden"}), 403
    
    drive = PlacementDrive.query.filter_by(id=id, status='APPROVED').first_or_404()
    
    # Check if already applied
    existing = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing:
        return jsonify({"message": "Already applied"}), 400
        
    # Deadline check
    if datetime.utcnow() > drive.application_deadline:
        return jsonify({"message": "Deadline has passed"}), 400

    new_app = Application(
        student_id=student.id,
        drive_id=drive.id,
        status='APPLIED'
    )
    db.session.add(new_app)
    db.session.commit()
    
    return jsonify({"message": "Successfully applied"}), 201

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    student = get_student()
    if not student: return jsonify({"message": "Forbidden"}), 403
    
    apps = Application.query.filter_by(student_id=student.id).all()
    res = [{
        "id": a.id,
        "drive_id": a.drive_id,
        "company": a.drive.company.company_name,
        "title": a.drive.title,
        "status": a.status,
        "applied_on": a.applied_at,
        "drive_description": a.drive.job_description,
        "drive_package": a.drive.package_details,
        "drive_location": a.drive.location,
        "offered_dates": a.offered_dates,
        "selected_date": a.selected_date
    } for a in apps]
    return jsonify(res), 200

@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    student = get_student()
    if not student: return jsonify({"message": "Forbidden"}), 403
    
    return jsonify({
        "full_name": student.full_name,
        "roll_number": student.roll_number,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "year": student.year
    }), 200

@student_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    student = get_student()
    if not student: return jsonify({"message": "Forbidden"}), 403
    
    data = request.get_json()
    if 'full_name' in data: student.full_name = data['full_name']
    if 'roll_number' in data: student.roll_number = data['roll_number']
    if 'branch' in data: student.branch = data['branch']
    if 'cgpa' in data: student.cgpa = float(data['cgpa'])
    if 'year' in data: student.year = int(data['year'])
    
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200

@student_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    student = get_student()
    if not student: return jsonify({"message": "Forbidden"}), 403
    
    from models.company import CompanyProfile
    companies = CompanyProfile.query.filter_by(approval_status='APPROVED').all()
    
    res = [{
        "id": c.id,
        "name": c.company_name,
        "description": c.description if c.description else "Information about " + c.company_name
    } for c in companies]
    
    return jsonify(res), 200

@student_bp.route('/export-history', methods=['GET'])
@jwt_required()
def export_history():
    student = get_student()
    if not student: return jsonify({"message": "Forbidden"}), 403
    
    from flask import Response
    import csv
    import io
    
    apps = Application.query.filter_by(student_id=student.id).all()
    
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
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=application_history.csv"}
    )

@student_bp.route('/applications/<int:id>/select_interview_date', methods=['PATCH'])
@jwt_required()
def select_interview_date(id):
    student = get_student()
    if not student: return jsonify({"message": "Forbidden"}), 403
    
    app_record = Application.query.filter_by(id=id, student_id=student.id).first_or_404()
    data = request.get_json()
    
    if not data or 'selected_date' not in data:
        return jsonify({"message": "Selected date is required"}), 400
        
    app_record.selected_date = datetime.strptime(data['selected_date'], '%Y-%m-%dT%H:%M')
    app_record.status = 'INTERVIEW_SCHEDULED'
    db.session.commit()
    
    return jsonify({"message": "Interview date confirmed successfully!"}), 200
