from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from models.student import StudentProfile
from models.company import CompanyProfile
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        if not user.is_active:
            return jsonify({"message": "Account is inactive."}), 403

        name = "Admin"
        if user.role == "STUDENT":
            student = StudentProfile.query.filter_by(user_id=user.id).first()
            if student: name = student.full_name
        elif user.role == "COMPANY":
            company = CompanyProfile.query.filter_by(user_id=user.id).first()
            if company: name = company.company_name

        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token, role=user.role, name=name), 200

    return jsonify({"message": "Invalid email or password"}), 401

@auth_bp.route('/student/register', methods=['POST'])
def register_student():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    roll_number = data.get('roll_number')
    branch = data.get('branch')
    cgpa = data.get('cgpa')
    year = data.get('year')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    # Create User
    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role='STUDENT'
    )
    db.session.add(new_user)
    db.session.flush() # to get new_user.id

    # Create Student Profile
    new_student = StudentProfile(
        user_id=new_user.id,
        full_name=full_name,
        roll_number=roll_number,
        branch=branch,
        cgpa=float(cgpa),
        year=int(year)
    )
    db.session.add(new_student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"}), 201

@auth_bp.route('/company/register', methods=['POST'])
def register_company():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    company_name = data.get('company_name')
    hr_contact_name = data.get('hr_contact_name')
    website = data.get('website')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role='COMPANY'
    )
    db.session.add(new_user)
    db.session.flush()

    new_company = CompanyProfile(
        user_id=new_user.id,
        company_name=company_name,
        hr_contact_name=hr_contact_name,
        hr_email=email,
        website=website,
        approval_status='PENDING'
    )
    db.session.add(new_company)
    db.session.commit()

    return jsonify({"message": "Company registered successfully. Waiting for admin approval."}), 201

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    profile_data = {
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }

    if user.role == 'STUDENT':
        student = StudentProfile.query.filter_by(user_id=user.id).first()
        if student:
            profile_data.update({
                "full_name": student.full_name,
                "roll_number": student.roll_number,
                "branch": student.branch,
                "cgpa": student.cgpa,
                "year": student.year
            })
    elif user.role == 'COMPANY':
        company = CompanyProfile.query.filter_by(user_id=user.id).first()
        if company:
            profile_data.update({
                "company_name": company.company_name,
                "approval_status": company.approval_status
            })

    return jsonify(profile_data), 200
