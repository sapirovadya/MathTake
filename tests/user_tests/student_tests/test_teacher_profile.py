import unittest
from flask import Flask, session, render_template_string, Blueprint, request
from flask_session import Session
import mongomock

class TeacherProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SECRET_KEY'] = 'supersecretkey'
        Session(self.app)
        self.client = self.app.test_client()

        # Create mock MongoDB
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client['test_database']
        self.db.teachers = self.db['teachers']

        # Insert a mock teacher
        self.teacher_data = {
            "name": "John Doe",
            "email": "teacher@example.com",
            "phone": "123456789",
            "grade_range": "5-8",
            "teacher_age": "35"
        }
        self.db.teachers.insert_one(self.teacher_data)

        # Create a mock blueprint
        self.mock_bp = Blueprint('student_bp', __name__)

        @self.mock_bp.route('/profile')
        def profile():
            teacher = self.db.teachers.find_one({"email": "teacher@example.com"})
            if not teacher:
                return "Teacher not found", 404

            return render_template_string("""
                <body>
                    <div class="centered-profile">
                        <div class="profile-container">
                            <h1 class="mb-4">Profile</h1>
                            <div class="row g-3">
                                <div class="col-sm-12">
                                    <div class="form-floating">
                                        <input id="name" name="name" class="form-control border-0" value="{{ teacher.name }}" readonly>
                                        <label for="name">Full name</label>
                                    </div>
                                </div>
                                <div class="col-sm-12">
                                    <div class="form-floating">
                                        <input id="email" name="email" class="form-control border-0" value="{{ teacher.email }}" readonly>
                                        <label for="email">Email address</label>
                                    </div>
                                </div>
                                <div class="col-sm-12">
                                    <div class="form-floating">
                                        <input id="phone" name="phone" class="form-control border-0" value="{{ teacher.phone }}" readonly>
                                        <label for="phone">Phone number</label>
                                    </div>
                                </div>
                                <div class="col-sm-12">
                                    <div class="form-floating">
                                        <input name="grade" class="form-control border-0" type="text" value="{{ teacher.grade_range }}" readonly>
                                        <label for="grade">Grade range</label>
                                    </div>
                                </div>
                                <div class="col-sm-12">
                                    <div class="form-floating">
                                        <input id="age" name="age" class="form-control border-0" value="{{ teacher.teacher_age }}" readonly>
                                        <label for="age">Age</label>
                                    </div>
                                </div>
                            </div>

                            <!-- Request Private Lesson Form -->
                            <div class="form-container">
                                <form action="{{ url_for('student_bp.private_lesson') }}" method="POST">
                                    <input type="hidden" name="teacher_email" value="{{ teacher.email }}">
                                    <input type="hidden" name="student_email" value="{{ session.get('email') }}">
                                    <button type="submit" class="btn btn-primary">Request Private Lesson</button>
                                </form>
                            </div>
                        </div>
                    </div>
            """, teacher=teacher)

        @self.mock_bp.route('/private_lesson', methods=['POST'])
        def private_lesson():
            teacher_email = request.form.get('teacher_email')
            student_email = request.form.get('student_email')

            if not student_email:
                return "Student not logged in", 401

            # Here you would handle the logic for requesting a private lesson
            # For the purpose of this test, we'll just return a success message
            return "Private lesson requested for teacher: " + teacher_email, 200

        self.app.register_blueprint(self.mock_bp)

    def tearDown(self):
        self.mongo_client.drop_database("test_database")

    def test_profile_display(self):
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'teacher@example.com', response.data)
        self.assertIn(b'123456789', response.data)
        self.assertIn(b'5-8', response.data)
        self.assertIn(b'35', response.data)

    def test_private_lesson_request(self):
        with self.client.session_transaction() as sess:
            sess['email'] = 'student@example.com'

        response = self.client.post('/private_lesson', data={
            'teacher_email': 'teacher@example.com',
            'student_email': 'student@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Private lesson requested for teacher: teacher@example.com', response.data)

if __name__ == '__main__':
    unittest.main()
