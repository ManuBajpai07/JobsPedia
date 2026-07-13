from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.company import CompanyProfile
from models.drive import PlacementDrive
from models.application import Application
from extensions import db
from datetime import datetime

company_bp = Blueprint('company', __name__)

def get_company():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'COMPANY':
        return None
    company = CompanyProfile.query.filter_by(user_id=user_id).first()
    return company

@company_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    company = get_company()
    if not company: return jsonify({"message": "Forbidden"}), 403
    
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    
    ongoing_drives = [d for d in drives if d.status == 'APPROVED']
    closed_drives = [d for d in drives if d.status in ['COMPLETED', 'CANCELLED']]
    ongoing_drive_ids = [d.id for d in ongoing_drives]
    
    total_applicants_ongoing = Application.query.filter(Application.drive_id.in_(ongoing_drive_ids)).count() if ongoing_drive_ids else 0

    stats = {
        "status": company.approval_status,
        "ongoing_drives": len(ongoing_drives),
        "closed_drives": len(closed_drives),
        "total_applicants_ongoing": total_applicants_ongoing
    }
    return jsonify(stats), 200

@company_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    company = get_company()
    if not company: return jsonify({"message": "Forbidden"}), 403
    
    return jsonify({
        "company_name": company.company_name,
        "hr_contact_name": company.hr_contact_name,
        "hr_email": company.hr_email,
        "website": company.website,
        "description": company.description
    }), 200

@company_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    company = get_company()
    if not company: return jsonify({"message": "Forbidden"}), 403
    
    data = request.get_json()
    if 'company_name' in data: company.company_name = data['company_name']
    if 'hr_contact_name' in data: company.hr_contact_name = data['hr_contact_name']
    if 'hr_email' in data: company.hr_email = data['hr_email']
    if 'website' in data: company.website = data['website']
    if 'description' in data: company.description = data['description']
    
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200

@company_bp.route('/drives', methods=['GET'])
@jwt_required()
def get_drives():
    company = get_company()
    if not company: return jsonify({"message": "Forbidden"}), 403
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    res = [{
        "id": d.id,
        "title": d.title,
        "status": d.status,
        "deadline": d.application_deadline,
        "location": d.location,
        "job_description": d.job_description,
        "branch_eligibility": d.branch_eligibility,
        "minimum_cgpa": d.minimum_cgpa,
        "eligible_year": d.eligible_year,
        "package_details": d.package_details
    } for d in drives]
    return jsonify(res), 200

@company_bp.route('/drives', methods=['POST'])
@jwt_required()
def create_drive():
    company = get_company()
    if not company: return jsonify({"message": "Forbidden"}), 403
    if company.approval_status != 'APPROVED':
        return jsonify({"message": "Company must be approved to create drives"}), 403

    data = request.get_json()
    new_drive = PlacementDrive(
        company_id=company.id,
        title=data.get('title'),
        job_description=data.get('job_description'),
        branch_eligibility=data.get('branch_eligibility'),
        minimum_cgpa=float(data.get('minimum_cgpa', 0)),
        eligible_year=int(data.get('eligible_year', 0)),
        application_deadline=datetime.strptime(data.get('application_deadline'), '%Y-%m-%d'),
        location=data.get('location'),
        package_details=data.get('package_details'),
        status='PENDING'
    )
    db.session.add(new_drive)
    db.session.commit()
    return jsonify({"message": "Drive created successfully"}), 201

@company_bp.route('/drives/<int:id>/applications', methods=['GET'])
@jwt_required()
def get_applications(id):
    company = get_company()
    if not company: return jsonify({"message": "Forbidden"}), 403
    
    drive = PlacementDrive.query.filter_by(id=id, company_id=company.id).first_or_404()
    apps = Application.query.filter_by(drive_id=drive.id).all()
    res = [{
        "id": a.id,
        "student_name": a.student.full_name,
        "student_email": a.student.user.email,
        "student_roll": a.student.roll_number,
        "student_branch": a.student.branch,
        "student_year": a.student.year,
        "cgpa": a.student.cgpa,
        "status": a.status
    } for a in apps]
    return jsonify(res), 200

@company_bp.route('/applications/<int:id>/status', methods=['PATCH'])
@jwt_required()
def update_application_status(id):
    company = get_company()
    if not company: return jsonify({"message": "Forbidden"}), 403
    
    app = Application.query.get_or_404(id)
    if app.drive.company_id != company.id:
        return jsonify({"message": "Forbidden"}), 403
        
    data = request.get_json()
    new_status = data.get('status')
    if new_status in ['SHORTLISTED', 'INTERVIEW_SCHEDULED', 'SELECTED', 'REJECTED']:
        app.status = new_status
        if new_status == 'SHORTLISTED' and 'offered_dates' in data:
            import json
            app.offered_dates = json.dumps(data['offered_dates'])
            
        db.session.commit()
        
        # Trigger background email notification
        try:
            from tasks import send_email_notification
            subject = f"Application Update: {app.drive.company.company_name}"
            body = f"Hello {app.student.full_name},\n\nYour application status for {app.drive.title} at {app.drive.company.company_name} has been updated to: {new_status}.\n\nBest,\nJobsPedia Team"
            send_email_notification.delay(app.student.user.email, subject, body)
        except Exception as e:
            print("Failed to dispatch email task:", e)
            
        return jsonify({"message": "Status updated successfully"}), 200
    return jsonify({"message": "Invalid status"}), 400

@company_bp.route('/drives/<int:id>/complete', methods=['PATCH'])
@jwt_required()
def complete_drive(id):
    company = get_company()
    if not company: return jsonify({"message": "Forbidden"}), 403
    
    drive = PlacementDrive.query.filter_by(id=id, company_id=company.id).first_or_404()
    drive.status = 'COMPLETED'
    db.session.commit()
    return jsonify({"message": "Drive marked as complete"}), 200

@company_bp.route('/drives/<int:id>', methods=['PATCH'])
@jwt_required()
def update_drive(id):
    company = get_company()
    if not company: return jsonify({"message": "Forbidden"}), 403
    
    drive = PlacementDrive.query.filter_by(id=id, company_id=company.id).first_or_404()
    data = request.get_json()
    
    if 'title' in data: drive.title = data['title']
    if 'job_description' in data: drive.job_description = data['job_description']
    if 'branch_eligibility' in data: drive.branch_eligibility = data['branch_eligibility']
    if 'minimum_cgpa' in data: drive.minimum_cgpa = float(data['minimum_cgpa'])
    if 'eligible_year' in data: drive.eligible_year = int(data['eligible_year'])
    if 'application_deadline' in data: drive.application_deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d')
    if 'location' in data: drive.location = data['location']
    if 'package_details' in data: drive.package_details = data['package_details']
    
    # Delete previous applications as this is a new cycle
    Application.query.filter_by(drive_id=id).delete()
    
    # Reset status to PENDING so it moves out of Closed Drives
    drive.status = 'PENDING'
    
    db.session.commit()
    return jsonify({"message": "Drive updated successfully"}), 200
