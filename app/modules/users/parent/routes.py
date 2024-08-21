from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
import pymongo
from modules.users.parent.models import Parent
from bson.objectid import ObjectId

# Create a blueprint named 'parent_bp'
parent_bp = Blueprint('parent_bp', __name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://Osnat:123456!@cluster1.7pvmkvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
db = client.get_database("total_records")

@parent_bp.route("/homepage", methods=['GET'])
def Parent_Index():
    return render_template("parent/indexParent.html")

@parent_bp.route('/profile', methods=['GET', 'POST'])
def profile_parent_form():
    if request.method == 'POST':
        old_email = session.get('email')
        updated_email = request.form.get("email")  # Get the new email from the form
        updated_data = {
            "name": request.form.get("name"),
            "email": updated_email,
            "phone": request.form.get("phone"),
            "password": request.form.get("password")
        }
        
        # Update the parent's data
        db.parents.update_one({"email": old_email}, {"$set": updated_data})
        
        # Update the parent_email in the students collection
        db.students.update_many({"parent_email": old_email}, {"$set": {"parent_email": updated_email}})
        
        # Update the email in the session
        session['email'] = updated_email

        return render_template("parent/indexParent.html", user=updated_data)
    
    else:
        email = session.get('email')
        user_data = db.parents.find_one({"email": email})
        if user_data:
            return render_template("parent/ParentProfile.html", user=user_data)
        else:
            return "User not found"




# @parent_bp.route('/profile', methods=['GET', 'POST'])
# def profile_parent_form():
#     if request.method == 'POST':
#         email = session.get('email')
#         updated_data = {
#             "name": request.form.get("name"),
#             "email": request.form.get("email"),
#             "phone": request.form.get("phone"),
#             "password": request.form.get("password")
#         }
#         db.parents.update_one({"email": email}, {"$set": updated_data})
#         return render_template("parent/indexParent.html", user=updated_data)
#     else:
#         email = session.get('email')
#         user_data = db.parents.find_one({"email": email})
#         if user_data:
#             return render_template("parent/ParentProfile.html", user=user_data)
#         else:
#             return "User not found"

@parent_bp.route("/MyStudent", methods=['GET'])
def MyStudent_form():
    # session['origin'] = 'MyStudentList'
    email = session.get('email')
    parent = db.parents.find_one({"email": email})
    if parent:
        students1 = []
        for student_email in parent.get('students', []):
            student = db.students.find_one({"email": student_email})
            if student:
                students1.append(student)

        return render_template("parent/MyStudentList.html", students=students1)
    else:
        return "Parent not found"
    

@parent_bp.route("/editstudentquestionnaire", methods=['GET'])
def edit_student_questionnaire():
    email = request.args.get('email')
    parent_email = request.args.get('parent_email')
    
    # Use the email to fetch the questionnaire data
    questionnaire_data = db.questionnaire.find_one({"student_email": email})
    
    if questionnaire_data:
        return render_template('parent/EditStudentQuestionnaire.html', questionnaire=questionnaire_data)
    else:
        return "Questionnaire not found"


@parent_bp.route("/updatestudentquestionnaire", methods=['POST'])
def update_studentb_questionnaire():
    form_data = request.form.to_dict()
    email = form_data.get('email')  # Use the hidden field from the form

    questionnaire_data = {
        "student_email": form_data.get('email'),
        "parent_email": form_data.get('parent_email'),
        "full_name": form_data.get('fullName'),
        "grade": form_data.get('grade'),
        "rating": form_data.get('rating'),
        "first_subject": form_data.get('firstSubject'),
        "second_subject": form_data.get('secondSubject'),
    }

    db.questionnaire.update_one({"student_email": email}, {"$set": questionnaire_data})
    return render_template('parent/indexParent.html')

@parent_bp.route("/Tips", methods=['GET'])
def Tips_page():
    return render_template("parent/Tips.html")


@parent_bp.route("/payment/<lesson_id>", methods=['GET'])
def payment_page(lesson_id):
    parent_email = session.get('email')
    if not parent_email:
        return redirect(url_for('login'))

    lesson = db.private_lesson.find_one({'_id': ObjectId(lesson_id), 'parent_email': parent_email})
    if not lesson:
        return redirect(url_for('parent_bp.lessons_payments_page'))

    return render_template("parent/payment.html", lesson=lesson)

@parent_bp.route('/lessons_payments')
def lessons_payments_page():
    parent_email = session.get('email')
    if not parent_email:
        return redirect(url_for('login'))

    lessons = db.private_lesson.find({'parent_email': parent_email})
    lessons_list = []
    for lesson in lessons:
        if lesson.get('date') and lesson.get('paid') == False:
            student = db.students.find_one({'email': lesson['student_email']})
            lesson['student_name'] = student['name'] if student else lesson['student_email']
            lessons_list.append(lesson)

    return render_template('parent/lessons_payments.html', lessons=lessons_list)

@parent_bp.route("/process_payment/<lesson_id>", methods=['POST'])
def process_payment(lesson_id):
    parent_email = session.get('email')
    if not parent_email:
        return redirect(url_for('login'))

    lesson = db.private_lesson.find_one({'_id': ObjectId(lesson_id), 'parent_email': parent_email})
    if not lesson:
        return redirect(url_for('parent_bp.lessons_payments_page'))

    db.private_lesson.update_one({'_id': ObjectId(lesson_id)}, {'$set': {'paid': True}})
    return redirect(url_for('parent_bp.Parent_Index'))




@parent_bp.route('/select_child_uploadQ', methods=['GET'])
def select_child_uploadQ():
    parent_email = session.get('email')
    parent = db.parents.find_one({'email': parent_email})
    children = parent.get('students', [])
    return render_template('parent/select_child_uploadQ.html', children=children)


@parent_bp.route("/uplod_question", methods=['GET'])
def upload_question():
    child_email = request.args.get('child_email')
    session['child_email'] = child_email  

    if not child_email:
        return redirect(url_for('parent_bp.select_child'))
    return render_template('parent/upload_question.html', child_email=child_email)
   

@parent_bp.route('/save_question', methods=['POST'])
def save_question():
    question = request.form.get('question')
    possible_answers = request.form.getlist('possible_answers[]')
    correct_answer = request.form.get('correct_answer')
    explanation = request.form.get('explanation')
    child_email = session.get('child_email')
    
    # Save to the database
    db.parentQuestion.insert_one({
        'child_email': child_email,
        'question': question,
        'possible_answers': possible_answers,
        'correct_answer': correct_answer,
        'explanation': explanation
    })

    action = request.form.get('action')
    
    if action == 'insert_another':
        return render_template('parent/upload_question.html', child_email=child_email)
    else:
        return redirect(url_for('parent_bp.some_confirmation_page'))



@parent_bp.route('/some_confirmation_page', methods=['GET'])
def some_confirmation_page():
    return render_template('parent/confirmation.html')

@parent_bp.route('/select_child', methods=['GET'])
def select_child():
    parent_email = session.get('email')
    parent = db.parents.find_one({'email': parent_email})
    children = parent.get('students', [])
    return render_template('parent/select_child.html', children=children)


@parent_bp.route("/progress", methods=['GET'])
def progress():
    student_email = request.args.get('student_email')
    return render_template('parent/progress.html', student_email=student_email)


@parent_bp.route('/show_progress', methods=['GET'])
def show_progress():
    child_email = request.args.get('child_email')
    if not child_email:
        return redirect(url_for('parent_bp.select_child'))

    # Fetch child's progress from both collections
    child_procss_data = db.childProcess.find_one({'student_email': child_email})
    tests_eval_data = db.testsEval.find_one({'student_email': child_email})

    if not child_procss_data and not tests_eval_data:
            return render_template('parent/progress.html', progress_data={}, child_email=child_email)

        
    if not child_procss_data:
        progress_data = {
            'tests_eval': tests_eval_data.get('answers', [])
        }

    elif not tests_eval_data:
        progress_data = {
            'child_procss': child_procss_data.get('answers', []),
    }
          
    else:
        # Combine and process data as needed for display
        progress_data = {
            'child_procss': child_procss_data.get('answers', []),
            'tests_eval': tests_eval_data.get('answers', [])
        }

    return render_template('parent/progress.html', progress_data=progress_data, child_email=child_email)

@parent_bp.route('/view_reports', methods=['GET'])
def view_reports():
    print("View reports route accessed.")  # Debugging line
    parent_email = session.get('email')
    if not parent_email:
        print("No email found in session.")  # Debugging line
        return render_template('parent/reports.html', error="No email found in session.")

    # Fetch the list of student emails from the parent table
    parent_record = db.parents.find_one({'email': parent_email})
    if not parent_record:
        print("No parent records found.")  # Debugging line
        return render_template('parent/reports.html', error="No parent records found.")

    student_emails = parent_record.get('students', [])
    if not student_emails:
        print("No student emails found for this parent.")  # Debugging line
        return render_template('parent/reports.html', error="No student emails found for this parent.")

    # Log for debugging
    print(f"Parent email: {parent_email}")
    print(f"Student emails: {student_emails}")

    # Fetch all reports where the student email matches
    reports = db.reports.find({'student_email': {'$in': student_emails}})
    report_list = []
    for report in reports:
        report_list.append({
            'teacher_email': report.get('teacher_email'),
            'student_email': report.get('student_email'),
            'date': report.get('date'),
            'content': report.get('report_content')
        })

    if not report_list:
        print("No reports available.")  # Debugging line

    return render_template('parent/reports.html', reports=report_list)
