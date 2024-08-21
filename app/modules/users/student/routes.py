from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import pymongo
import modules.users.student.utils as util
from modules.users.models import User
from modules.users.student.models import Student 
import random

# from datetime import datetime
# import datetime
from datetime import datetime

student_bp = Blueprint('student_bp', __name__)

# MongoDB connection setup
client = pymongo.MongoClient("mongodb+srv://Osnat:123456!@cluster1.7pvmkvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
db = client.get_database("total_records")
students_collection = db.students  # Assuming 'students' collection
questionnaire_collection = db.questionnaire
parentQuestion_collection = db.parentQuestion
correct_or_not = None
previous_question = None
 
@student_bp.route("/indexStudent", methods=['GET'])
def displayStudentHome():
    return render_template('student/indexStudent.html')

@student_bp.route("/questionnaire", methods=['GET'])
def questionnaire():
    email = request.args.get('email')

    student1 = db.students.find_one({"email": email})  # Adjust query as per your data structure
    return render_template('student/questionnaire.html', student=student1)


@student_bp.route("/submit_questionnaire", methods=['POST'])
def submit_questionnaire():
    form_data = request.form.to_dict()

    questionnaire_data = {
        "student_email": form_data.get('email'),
        "parent_email": form_data.get('parent_email'),
        "full_name": form_data.get('fullName'),
        "grade": form_data.get('grade'),
        "rating": form_data.get('rating'),
        "first_subject": form_data.get('firstSubject'),
        "second_subject": form_data.get('secondSubject'),
    }
    questionnaire_collection.insert_one(questionnaire_data)
    

    # Redirect to home page for Student or wherever appropriate
    return render_template('index.html')


@student_bp.route("/editquestionnaire/<email>/<parent_email>", methods=['GET'])
def edit_questionnaire(email, parent_email):
    # Use the email to fetch the questionnaire data
    questionnaire_data = db.questionnaire.find_one({"student_email": email})
    
    if questionnaire_data:
        return render_template('student/EditMyQuestionnaire.html', questionnaire=questionnaire_data)
    else:
        return "Questionnaire not found"

@student_bp.route("/updatequestionnaire", methods=['POST'])
def update_questionnaire():
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
    return render_template('student/indexStudent.html')





@student_bp.route('/myprofile', methods=['GET', 'POST'])
def profile_student_form():
    if request.method == 'POST':
        email = session.get('email')
        updated_email = request.form.get("email")  # Get the new email from the form
        updated_data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "parent_email": request.form.get("parent_email"),
            "password": request.form.get("password")
        }
        
        db.students.update_one({"email": email}, {"$set": updated_data})
        db.questionnaire.update_one({"student_email": email}, {"$set": {"parent_email": request.form.get("parent_email"), "student_email": request.form.get("email"), "full_name": request.form.get("name")}})
       
        db.parents.update_one({"students": email}, {"$set": {"students.$": updated_email}})

        session['email'] = updated_email
        return render_template("student/indexStudent.html", student=updated_data)
    
    else:
        email = session.get('email')
        student1 = db.students.find_one({"email": email})
        if student1:
            return render_template("student/StudentProfile.html", student=student1)
        else:
            return "User not found"



@student_bp.route("/mathQuiz", methods=['GET'])
def mathQuiz():
    student_email = session.get('email')
    random_choice = random.randint(0, 1)

    if random_choice == 0:
        parent_question = parentQuestion_collection.find_one({"child_email": student_email})
        if parent_question:
            question = parent_question['question']
            possibleAnswers = parent_question['possible_answers']
            correctAnswer = parent_question['correct_answer']
            explanation = parent_question['explanation']
            
            # Delete the question after fetching it
            parentQuestion_collection.delete_one({"_id": parent_question['_id']})

            return render_template('student/mathQuiz.html',question=question,ans1=possibleAnswers[0],ans2=possibleAnswers[1],ans3=possibleAnswers[2],ans4=possibleAnswers[3],correctAnswer=correctAnswer,explanation=explanation)

    # If no parent question is found or random_choice is 1, generate a question using the AI API
    student = questionnaire_collection.find_one({"student_email": student_email})
    if correct_or_not != None and previous_question != None:
        if correct_or_not == 1:   # more difficult question
            question_dict = util.generate_questions(dict(student), 1 , "difficult" , previous_question )[0]
            question, possibleAnswers, correctAnswer, explanation = question_dict['question'], question_dict['possible_answers'], question_dict['correct_answer'], question_dict['explanation']
            previous_question = question_dict
            return render_template('student/mathQuiz.html',question=question,ans1=possibleAnswers[0],ans2=possibleAnswers[1],ans3=possibleAnswers[2],ans4=possibleAnswers[3],correctAnswer=correctAnswer,explanation=explanation)
        
        if correct_or_not == 0:  # more simpler question
            question_dict = util.generate_questions(dict(student), 1 , "simpler" , previous_question )[0]
            question, possibleAnswers, correctAnswer, explanation = question_dict['question'], question_dict['possible_answers'], question_dict['correct_answer'], question_dict['explanation']
            previous_question = question_dict
            return render_template('student/mathQuiz.html',question=question,ans1=possibleAnswers[0],ans2=possibleAnswers[1],ans3=possibleAnswers[2],ans4=possibleAnswers[3],correctAnswer=correctAnswer,explanation=explanation)
    
    # else - there is no previous question
    question_dict = util.generate_questions(dict(student), 1)[0]
    question, possibleAnswers, correctAnswer, explanation = question_dict['question'], question_dict['possible_answers'], question_dict['correct_answer'], question_dict['explanation']
    previous_question = question_dict
    return render_template('student/mathQuiz.html',question=question,ans1=possibleAnswers[0],ans2=possibleAnswers[1],ans3=possibleAnswers[2],ans4=possibleAnswers[3],correctAnswer=correctAnswer,explanation=explanation)
            


@student_bp.route("/submit-answer", methods=['POST'])
def submit_answer():
    student_answer = request.form['answer']
    correct_answer = request.form['correctAnswer']
    explanation = request.form['explanation']
    print(f"request={request.form}")
    print(f"student_answer={student_answer}, correct_answer={correct_answer}")
    is_correct = student_answer == correct_answer
    childProcess = db.childProcess
    correct_or_not = is_correct
    
    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Find the student's document
    student_email = session.get('email')
    student_doc = childProcess.find_one({"student_email": student_email})

    if student_doc:
        # Check if there's an entry for the current date
        date_entry = next((entry for entry in student_doc['answers'] if entry['date'] == current_date), None)
        if date_entry:
            # Update the existing date entry
            if is_correct:
                date_entry['correct'] += 1
            else:
                date_entry['incorrect'] += 1
        else:
            # Add a new entry for the current date
            new_entry = {
                "date": current_date,
                "correct": 1 if is_correct else 0,
                "incorrect": 0 if is_correct else 1
            }
            student_doc['answers'].append(new_entry)
        
        student_doc_bfore = childProcess.find_one({"student_email": student_email})
        # Update the document in the database
        childProcess.update_one(
            {"student_email": student_email},
            {"$set": {"answers": student_doc['answers']}}
        )
        student_doc_after = childProcess.find_one({"student_email": student_email})
        print(student_doc_bfore)
        print(student_doc_after)
    else:
        # Create a new document for the student
        new_student_doc = {
            "student_email": student_email,
            "answers": [
                {
                    "date": current_date,
                    "correct": 1 if is_correct else 0,
                    "incorrect": 0 if is_correct else 1
                }
            ]
        }
        childProcess.insert_one(new_student_doc)

    result = {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "explanation": explanation
    }
    
    return jsonify(result)


@student_bp.route("/teachers")
def list_teachers():
    teachers = db.teachers.find()
    return render_template("student/team.html", teachers=teachers)

@student_bp.route('/teacher/<email>', methods=['GET'])
def teacher_profile(email):
    teacher = db.teachers.find_one({"email": email})
    if teacher:
        student_email = session.get('email')
        return render_template(
            "student/teacher_profile.html",
            teacher=teacher,
            student_email=student_email,
        )
    else:
        return "Teacher not found", 404


@student_bp.route("/private_lesson", methods=['POST'])
def private_lesson():
    form_data = request.form.to_dict()
    teacher_email = form_data.get('teacher_email')
    student_email = session.get('email')
    student = db.students.find_one({"email": student_email})
    if student:
        parent_email = student.get('parent_email')
    else:
        parent_email = None
    
    private_lesson_data = {
        "teacher_email": teacher_email,
        "student_email": student_email,
        "parent_email": parent_email,
        "paid": False,
        "date": None,
        "time": None
    }
    db.private_lesson.insert_one(private_lesson_data)
    return redirect(url_for('student_bp.displayStudentHome'))


tests = []

@student_bp.route('/buildTest', methods=['GET', 'POST'])
def buildTest():
    if request.method == 'POST':
        student = questionnaire_collection.find_one({"student_email": session.get('email')})
        data = request.form.to_dict()
        data['grade'] = (dict(student))['grade']
        questions = util.generate_questions(data, int(data['num_questions']))
        global tests
        tests = questions
        return redirect(url_for('student_bp.solveTest'))
    return render_template('student/buildTest.html')


@student_bp.route('/solveTest', methods=['GET', 'POST'])
def solveTest():
    global tests
    if request.method == 'POST':
        answers = request.form.to_dict()
        results = []
        correct_count = 0
        for question in tests:
            user_answer = answers.get(question['question'])
            correct = (user_answer == question['correct_answer'])
            if correct:
                correct_count += 1
            results.append({
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'explanation': question['explanation'],
                'correct': correct
            })

        # Update the student's test evaluation
        testsEval = db.testsEval
        current_date = datetime.now().strftime("%Y-%m-%d")
        student_doc = testsEval.find_one({"student_email": session.get('email')})

        if student_doc:
            date_entry = next((entry for entry in student_doc['answers'] if entry['date'] == current_date), None)
            if date_entry:
                date_entry['correct'] += correct_count
                date_entry['incorrect'] += (len(tests) - correct_count)
            else:
                new_entry = {
                    "date": current_date,
                    "correct": correct_count,
                    "incorrect": (len(tests) - correct_count)
                }
                student_doc['answers'].append(new_entry)
            
            testsEval.update_one(
                {"student_email": session.get('email')},
                {"$set": {"answers": student_doc['answers']}}
            )
        else:
            new_student_doc = {
                "student_email": session.get('email'),
                "answers": [
                    {
                        "date": current_date,
                        "correct": correct_count,
                        "incorrect": (len(tests) - correct_count)
                    }
                ]
            }
            testsEval.insert_one(new_student_doc)
        
        grade = (100/len(tests)) * correct_count

        # Remove the test from the database after solving
        db.teacherTestForStudent.delete_one({
            "student_email": session.get('email'),
            "questions": tests
        })

        return render_template('student/solveTest.html', results=results, grade = grade )
    
    return render_template('student/solveTest.html', questions=tests)



@student_bp.route('/privateLessons')
def student_private_lessons():
    student_email = session.get('email')
    if not student_email:
        return redirect(url_for('login'))

    lessons = db.private_lesson.find({'student_email': student_email, 'paid': True})
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

    return render_template('student/privateLessons.html', lessons=lessons_list)


@student_bp.route('/select_test', methods=['GET'])
def test_from_teacher():
    return redirect(url_for('student_bp.take_teacher_test'))


@student_bp.route('/take_teacher_test', methods=['GET'])
def take_teacher_test():
    student_email = session.get('email')
    
    # Fetch the test from the database
    test_doc = db.teacherTestForStudent.find_one({"student_email": student_email})

    if test_doc:
        global tests
        tests = test_doc['questions']
        return redirect(url_for('student_bp.solveTest'))
    else:
        return render_template('student/no_test_found.html')

@student_bp.route('/view_posts', methods=['GET'])
def view_posts():
    # Retrieve posts sorted by date in descending order
    posts = db.posts.find().sort("date", -1)
    return render_template("student/view_posts.html", posts=posts)