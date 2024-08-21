from flask import Blueprint, render_template, request, redirect, url_for, session
import pymongo
from modules.users.student.models import Student
from modules.users.teacher.models import Teacher
from modules.users.parent.models import Parent
import modules.users.utils as utils

# Create a blueprint named 'users_bp'
users_bp_main = Blueprint('users_bp_main', __name__)

client = pymongo.MongoClient("mongodb+srv://Osnat:123456!@cluster1.7pvmkvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
db = client.get_database("total_records")


@users_bp_main.route("/home", methods=['GET'])
def Home():
    return render_template("index.html")

@users_bp_main.route("/signup", methods=['GET'])
def signup_form():
    return render_template("signupPage.html")


# @users_bp_main.route('/student_questionnaire', methods=['GET', 'POST'])
# def view_student_questionnaire():
#     email = request.args.get('email')
#     origin = session.get('origin') 
#     student = db.students.find_one({"email": email})

#     if origin == 'MyStudentList':
#         email = request.args.get('email')
#         if request.method == 'POST':
#             updated_questionnaire_data = {
#                 "student_email": request.form.get('email'),
#                 "parent_email": request.form.get('parent_email'),
#                 "full_name": request.form.get('fullName'),
#                 "grade": request.form.get('grade'),
#                 "rating": request.form.get('rating'),
#                 "first_subject": request.form.get('firstSubject'),
#                 "second_subject": request.form.get('secondSubject'),
#             }
#             db.questionnaire.update_one({"email": email}, {"$set": updated_questionnaire_data})
#             return redirect(url_for('parent/indexParent'))
#         else:
#             email = request.args.get('email')
#             questionnaire_data = db.questionnaire.find_one({"email": email})
#             if questionnaire_data:
#                 return render_template("student/questionnaire.html", student=questionnaire_data)
#     elif origin == 'signuppage':
#         return redirect(url_for('student.bp.questionnaire'))
#     else:
#         return "User not found"

#     return render_template('student/questionnaire.html', student=student)

@users_bp_main.route("/signup", methods=['POST'])
def signup():
    data = request.form.to_dict()
    email = data.get('email')

    if not utils.verify_name(data.get('name')):
        return render_template("signupPage.html", error="Name must contain only English letters.", form_data=data)

    # Validate phone number
    if not utils.verify_phone_number(data.get('phone')):
        return render_template("signupPage.html", error="Phone number must consist of exactly 10 digits.", form_data=data)

    # Validate password
    if not utils.verify_password(data.get('password')):
        return render_template("signupPage.html", error="Password must be at least 6 characters long and contain at least one letter and one digit.", form_data=data)

    if db.parents.find_one({"email": email}) or db.teachers.find_one({"email": email}) or db.students.find_one({"email": email}):
        return render_template("signupPage.html", error="Email already exists. Please use a different email.", form_data=data)

    if data.get('role') == 'Student':
        parent_email = data.get('parent_email')
        parent = db.parents.find_one({"email": parent_email, "role": "Parent"})
        if not parent:
            return render_template("signupPage.html", error="Parent email not found. Please provide a valid parent email.", form_data=data)

        db.parents.update_one({"email": parent_email}, {"$addToSet": {"students": data['email']}})
        data["parent_email"] = parent_email
        
        user = Student().signup(data)
        db.students.insert_one(user)
        session['origin'] = 'signuppage'
        return redirect(url_for('student_bp.questionnaire', email=data['email']))
    
    elif data.get('role') == 'Parent':
        user = Parent().signup(data)
        db.parents.insert_one(user)
    
    else:
        grade_range = data.get('grade_range')
        teacher_age = data.get('teacher_age')
        user = Teacher().signup(data)
        user["grade_range"] = grade_range
        user["teacher_age"] = teacher_age
        db.teachers.insert_one(user)
    
    return redirect(url_for('home'))


@users_bp_main.route("/login", methods=['GET'])
def login_form():
    return render_template("login.html")

@users_bp_main.route("/login", methods=['POST'])
def login():
    data = request.form
    email = data.get('email')
    password = data.get('password')

    parent = db.parents.find_one({"email": email, "password": password})
    if parent:
        session['email'] = email
        session['name'] = parent.get('name')  # Assuming 'name' is a field in the parents collection
        return render_template('parent/indexParent.html')

    teacher = db.teachers.find_one({"email": email, "password": password})
    if teacher:
        session['email'] = email
        session['name'] = teacher.get('name')  # Assuming 'name' is a field in the teachers collection
        return render_template('teacher/indexTeacher.html')

    student = db.students.find_one({"email": email, "password": password})
    if student:
        session['email'] = email
        session['name'] = student.get('name')  # Assuming 'name' is a field in the students collection
        return render_template('student/indexStudent.html')

    # If login fails, pass back the email and an error message
    return render_template("login.html", error="Invalid username or password.", email=email)

@users_bp_main.route("/FQA", methods=['GET'])
def FQA_page():
    return render_template("FQA.html")
