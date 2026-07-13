from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.company import CompanyProfile
from models.student import StudentProfile
from models.drive import PlacementDrive
from models.application import Application
from extensions import db, cache

admin_bp = Blueprint('admin', __name__)

def admin_required():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'ADMIN':
        return False
    return True

# --- Users (Blacklist) ---
@admin_bp.route('/users/<int:user_id>/toggle_status', methods=['PATCH'])
@jwt_required()
def toggle_user_status(user_id):
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    user = User.query.get_or_404(user_id)
    if user.role == 'ADMIN': return jsonify({"message": "Cannot toggle admin"}), 400
    
    # Toggle active status
    user.is_active = not user.is_active
    
    # If blacklisted and it's a company, cancel their drives
    if not user.is_active and user.role == 'COMPANY':
        company = CompanyProfile.query.filter_by(user_id=user.id).first()
        if company:
            drives = PlacementDrive.query.filter_by(company_id=company.id).all()
            for d in drives:
                if d.status in ['APPROVED', 'PENDING']:
                    d.status = 'CANCELLED'
    db.session.commit()
    return jsonify({"message": "Status updated", "is_active": user.is_active}), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    user = User.query.get_or_404(user_id)
    if user.role == 'ADMIN': return jsonify({"message": "Cannot delete admin"}), 400
    
    if user.role == 'STUDENT':
        student = StudentProfile.query.filter_by(user_id=user.id).first()
        if student:
            Application.query.filter_by(student_id=student.id).delete()
    elif user.role == 'COMPANY':
        company = CompanyProfile.query.filter_by(user_id=user.id).first()
        if company:
            drives = PlacementDrive.query.filter_by(company_id=company.id).all()
            for d in drives:
                Application.query.filter_by(drive_id=d.id).delete()
                db.session.delete(d)
                
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User and associated data deleted successfully"}), 200

# --- Companies ---
@admin_bp.route('/companies/registered', methods=['GET'])
@jwt_required()
def get_registered_companies():
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    query = request.args.get('search', '')
    companies = CompanyProfile.query.join(User).filter(CompanyProfile.approval_status == 'APPROVED')
    if query:
        companies = companies.filter(CompanyProfile.company_name.ilike(f'%{query}%'))
    res = [{
        "id": c.id, 
        "user_id": c.user_id,
        "name": c.company_name, 
        "contact": c.hr_contact_name,
        "email": c.hr_email,
        "website": c.website,
        "is_active": c.user.is_active
    } for c in companies.all()]
    return jsonify(res), 200

@admin_bp.route('/companies/pending', methods=['GET'])
@jwt_required()
def get_pending_companies():
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    companies = CompanyProfile.query.filter_by(approval_status='PENDING').all()
    res = [{
        "id": c.id, 
        "name": c.company_name
    } for c in companies]
    return jsonify(res), 200

@admin_bp.route('/companies/<int:id>/approve', methods=['PATCH'])
@jwt_required()
def approve_company(id):
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    company = CompanyProfile.query.get_or_404(id)
    company.approval_status = 'APPROVED'
    # Auto-approve any pending drives for simplicity
    drives = PlacementDrive.query.filter_by(company_id=company.id, status='PENDING').all()
    for d in drives:
        d.status = 'APPROVED'
    db.session.commit()
    return jsonify({"message": "Company and their drives approved"}), 200

# --- Students ---
@admin_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    query = request.args.get('search', '')
    students = StudentProfile.query.join(User)
    if query:
        students = students.filter(StudentProfile.full_name.ilike(f'%{query}%'))
    res = [{
        "id": s.id, 
        "user_id": s.user_id,
        "name": s.full_name,
        "roll_number": s.roll_number,
        "branch": s.branch,
        "cgpa": s.cgpa,
        "year": s.year,
        "is_active": s.user.is_active
    } for s in students.all()]
    return jsonify(res), 200

# --- Drives ---
@admin_bp.route('/drives/ongoing', methods=['GET'])
@jwt_required()
def get_ongoing_drives():
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    drives = PlacementDrive.query.filter_by(status='APPROVED').all()
    res = [{
        "id": d.id, 
        "company": d.company.company_name,
        "title": d.title, 
        "description": d.job_description,
        "salary": d.package_details,
        "location": d.location
    } for d in drives]
    return jsonify(res), 200

@admin_bp.route('/drives/pending', methods=['GET'])
@jwt_required()
def get_pending_drives():
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    drives = PlacementDrive.query.filter_by(status='PENDING').all()
    res = [{
        "id": d.id, 
        "company": d.company.company_name,
        "title": d.title, 
        "deadline": d.application_deadline
    } for d in drives]
    return jsonify(res), 200

@admin_bp.route('/drives/<int:id>/approve', methods=['PATCH'])
@jwt_required()
def approve_drive(id):
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'APPROVED'
    db.session.commit()
    return jsonify({"message": "Drive approved successfully"}), 200

@admin_bp.route('/drives/<int:id>/reject', methods=['PATCH'])
@jwt_required()
def reject_drive(id):
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'REJECTED'
    db.session.commit()
    return jsonify({"message": "Drive rejected successfully"}), 200

@admin_bp.route('/drives/<int:id>/complete', methods=['PATCH'])
@jwt_required()
def complete_drive(id):
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'COMPLETED'
    db.session.commit()
    return jsonify({"message": "Drive marked as complete"}), 200

# --- Applications ---
@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    apps = Application.query.all()
    res = [{
        "id": a.id, 
        "student_name": a.student.full_name,
        "student_branch": a.student.branch,
        "student_roll": a.student.roll_number,
        "student_cgpa": a.student.cgpa,
        "student_year": a.student.year,
        "student_is_active": a.student.user.is_active,
        "drive_title": a.drive.title,
        "company_name": a.drive.company.company_name,
        "date": a.applied_at.strftime('%d/%m/%Y'),
        "status": a.status
    } for a in apps]
    return jsonify(res), 200

@admin_bp.route('/drives/<int:id>/applications', methods=['GET'])
@jwt_required()
def get_drive_applications(id):
    if not admin_required(): return jsonify({"message": "Forbidden"}), 403
    drive = PlacementDrive.query.get_or_404(id)
    apps = Application.query.filter_by(drive_id=drive.id).all()
    res = [{
        "id": a.id, 
        "student_name": a.student.full_name,
        "student_branch": a.student.branch,
        "student_roll": a.student.roll_number,
        "student_cgpa": a.student.cgpa,
        "student_year": a.student.year,
        "student_is_active": a.student.user.is_active,
        "status": a.status,
        "date": a.applied_at.strftime('%d/%m/%Y')
    } for a in apps]
    return jsonify(res), 200
