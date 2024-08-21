from datetime import datetime
from flask import Blueprint, Response, render_template, request, redirect, url_for, session
import pymongo
from modules.users.teacher.models import Teacher
from bson.objectid import ObjectId


teacher_bp = Blueprint('teacher_bp', __name__)

client = pymongo.MongoClient("mongodb+srv://Osnat:123456!@cluster1.7pvmkvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
db = client.get_database("total_records")

@teacher_bp.route("/homepage", methods=['GET'])
def Teacher_Index():
    return render_template("teacher/indexTeacher.html")

@teacher_bp.route('/teacherprofile', methods=['GET', 'POST'])
def profile_teacher_form():
    if request.method == 'POST':
        email = session.get('email')
        updated_data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "password": request.form.get("password")
        }
        db.teachers.update_one({"email": email}, {"$set": updated_data})
        return render_template("teacher/indexTeacher.html", teacher=updated_data)
    else:
        email = session.get('email')
        teacher1 = db.teachers.find_one({"email": email})
        if teacher1:
            return render_template("teacher/TeacherProfile.html", teacher=teacher1)
        else:
            return "User not found"
        

@teacher_bp.route('/privateLesson')
def teacher_private_lessons():
    teacher_email = session.get('email')
    if not teacher_email:
        return redirect(url_for('login'))
    
    lessons = db.private_lesson.find({'teacher_email': teacher_email, 'paid': True})
    lessons_list = []
    current_date = datetime.now()

    for lesson in lessons:
        lesson_date_str = lesson.get('date')
        lesson_time_str = lesson.get('time')
        
        if lesson_date_str and lesson_time_str:
            lesson_datetime_str = f"{lesson_date_str} {lesson_time_str}"
            lesson_datetime = datetime.strptime(lesson_datetime_str, "%d-%m-%Y %H:%M")
            if lesson_datetime >= current_date:
                lessons_list.append(lesson)

    return render_template('teacher/privateLesson.html', lessons=lessons_list)


@teacher_bp.route('/scheduling', methods=['GET'])
def scheduling():
    teacher_email = session.get('email')  # Assuming the teacher's email is stored in the session
    if not teacher_email:
        return "Teacher not logged in", 403

    # Fetch lessons for the teacher where 'date' field is null or not set
    lessons = db.private_lesson.find({
        "teacher_email": teacher_email,
        "$or": [
            {"date": {"$exists": False}},
            {"date": None}
        ],
        "$or": [
            {"time": {"$exists": False}},
            {"time": None}
        ]
    })

    lessons_list = list(lessons)  # Convert cursor to list for rendering
    return render_template('teacher/schedule.html', lessons=lessons_list)
    

@teacher_bp.route('/schedule_lesson', methods=['POST'])
def schedule_lesson():
    student_email = request.form.get('student_email')
    date_str = request.form.get('date')
    time_str = request.form.get('time')


    if not student_email or not date_str or not time_str:
        return Response('{"status": "error", "message": "Missing data"}', status=400, mimetype='application/json')

    try:
        # Update lessons for the student with the given email
        result = db.private_lesson.update_many(
            {'student_email': student_email, 'date': {'$in': [None, ""]}, 'time': {'$in': [None, ""]}},
            {'$set': {'date': date_str, 'time': time_str}}
        )


        if result.matched_count == 0:
            return Response('{"status": "error", "message": "No lessons found for the student"}', status=404, mimetype='application/json')

        return Response('{"status": "success", "message": "Lessons scheduled successfully!"}', status=200, mimetype='application/json')

    except Exception as e:
        return Response(f'{{"status": "error", "message": "{str(e)}"}}', status=500, mimetype='application/json')


@teacher_bp.route('/select_student', methods=['GET'])
def select_student():
    teacher_email = session.get('email')
    today = datetime.now()

    # Fetch all records for the teacher
    all_lessons = db.private_lesson.find({
        'teacher_email': teacher_email,
        'paid': True
    })

    print('all_lessons' , all_lessons)

    eligible_students = []
    for lesson in all_lessons:
        print('lession',lesson)
        lesson_date_str = lesson.get('date')
        
        # Convert the date string to a datetime object if it is not 'null'
        if lesson_date_str and lesson_date_str.lower() != 'null':
            try:
                lesson_date = datetime.strptime(lesson_date_str, '%d-%m-%Y')  # Assuming date format is 'DD-MM-YYYY'
                if lesson_date < today:
                    eligible_students.append(lesson['student_email'])
            except ValueError:
                # Handle the case where the date string is not in the expected format
                print(f"Date format error: {lesson_date_str}")

    print(eligible_students)
    
    return render_template('teacher/select_student.html', students=eligible_students)


@teacher_bp.route('/build_test', methods=['GET'])
def build_test():
    student_email = request.args.get('student_email')
    if not student_email:
        return redirect(url_for('teacher_bp.select_student'))
    
    # Save the selected student in the session
    session['selected_student'] = student_email

    return render_template('teacher/build_test.html', student_email=student_email)



@teacher_bp.route('/save_test', methods=['POST'])
def save_test():
    student_email = session.get('selected_student')
    if not student_email:
        return redirect(url_for('teacher_bp.select_student'))
    
    # Extract the number of questions
    num_questions = int(request.form.get('numQuestions', 0))
    
    # Initialize a list to store formatted questions
    formatted_questions = []

    # Loop through each question based on the number of questions specified
    for i in range(1, num_questions + 1):
        question = request.form.get(f'questions[{i}][question]')
        option1 = request.form.get(f'questions[{i}][option1]')
        option2 = request.form.get(f'questions[{i}][option2]')
        option3 = request.form.get(f'questions[{i}][option3]')
        option4 = request.form.get(f'questions[{i}][option4]')
        correct_answer = request.form.get(f'questions[{i}][correct_answer]')
        explanation = request.form.get(f'questions[{i}][explanation]')

        # Add the formatted question to the list
        formatted_questions.append({
            'question': question,
            'possible_answers': [option1, option2, option3, option4],
            'correct_answer': correct_answer,
            'explanation': explanation
        })

    # Save to the database
    db.teacherTestForStudent.insert_one({
        'student_email': student_email,
        'questions': formatted_questions
    })

    return render_template("teacher/indexTeacher.html")

from datetime import datetime

@teacher_bp.route('/posts', methods=['POST'])
def create_post():
    # Retrieve the post content and writer's name
    writer_name = session.get('name')
    post_content = request.form.get('post_content')
    post_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Writer Name: {writer_name}")
    print(f"Post Content: {post_content}")
    print(f"Post Date: {post_date}")
    
    if writer_name and post_content:
        new_post = {
            "content": post_content,
            "writer_name": writer_name,
            "date": post_date
        }
        try:
            db.posts.insert_one(new_post)
            print("Post saved successfully")
            return redirect(url_for('teacher_bp.view_posts'))
        except Exception as e:
            print(f"Error saving post: {e}")
    else:
        print("Post content or writer name is missing")

    return redirect(url_for('teacher_bp.view_posts'))

@teacher_bp.route('/view_salary')
def view_salary():
    teacher_email = session.get('email')
    today = datetime.now()

    # Fetch all lessons for the teacher
    all_lessons = db.private_lesson.find({
        'teacher_email': teacher_email,
        'paid': True
    })

    num_lessons = 0
    lesson_rate = 90  # Fixed rate per lesson
    total_earnings = 0

    for lesson in all_lessons:
        lesson_date_str = lesson.get('date')
        
        # Convert the date string to a datetime object if it is not 'null'
        if lesson_date_str and lesson_date_str.lower() != 'null':
            try:
                lesson_date = datetime.strptime(lesson_date_str, '%d-%m-%Y')  # Assuming date format is 'DD-MM-YYYY'
                if lesson_date < today:
                    num_lessons += 1
            except ValueError:
                # Handle the case where the date string is not in the expected format
                print(f"Date format error: {lesson_date_str}")

    total_earnings = num_lessons * lesson_rate

    return render_template('teacher/view_salary.html', num_lessons=num_lessons, lesson_rate=lesson_rate, total_earnings=total_earnings)


@teacher_bp.route('/student_report', methods=['GET'])
def student_report():
    teacher_email = session.get('email')
    today = datetime.now()

    # Fetch all lessons for the teacher
    all_lessons = db.private_lesson.find({
        'teacher_email': teacher_email,
        'date': {'$lt': today.strftime('%d-%m-%Y')},
        'paid': True
    })

    # Use a set to store unique student emails
    student_emails = set()
    for lesson in all_lessons:
        student_emails.add(lesson['student_email'])

    return render_template('teacher/student_report.html', student_emails=sorted(student_emails))

@teacher_bp.route('/submit_report', methods=['POST'])
def submit_report():
    teacher_email = session.get('email')
    student_email = request.form.get('student_email')
    report_content = request.form.get('report_content')

    if not teacher_email or not student_email or not report_content:
        return render_template('teacher/student_report.html', error="All fields are required.")

    report = {
        'teacher_email': teacher_email,
        'student_email': student_email,
        'report_content': report_content,
        'date': datetime.now().strftime('%d-%m-%Y')  # Save the current date
    }

    try:
        # Insert the report into the database
        db.reports.insert_one(report)
        
        # Delete the row from the private_lesson table
        db.private_lesson.delete_one({
            'teacher_email': teacher_email,
            'student_email': student_email,
            'date': {'$lt': datetime.now().strftime('%d-%m-%Y')},
            'paid': True
        })
        
        return redirect(url_for('teacher_bp.student_report'))
    except Exception as e:
        return render_template('teacher/student_report.html', error=f"Error saving report: {e}")
    
@teacher_bp.route('/posts', methods=['GET'])
def view_posts():
    # Retrieve posts sorted by date in descending order
    posts = db.posts.find().sort("date", -1)
    return render_template("teacher/posts.html", posts=posts)