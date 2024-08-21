import unittest
from flask import Flask, session, render_template_string, Blueprint
from flask_session import Session
import mongomock

class TeacherZoomLessonTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SECRET_KEY'] = 'supersecretkey'
        Session(self.app)
        self.client = self.app.test_client()

        #Create mock MongoDB
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client['test_database']
        self.db.private_lesson = self.db['private_lesson']

        # Insert mock lessons
        self.db.private_lesson.insert_many([
            {
                "teacher_email": "teacher@example.com",
                "student_email": "student1@example.com",
                "parent_email": "parent@example.com",
                "paid": True,
                "date": "20-10-2024",
                "time": "14:00"
            },
            {
                "teacher_email": "teacher@example.com",
                "student_email": "student2@example.com",
                "parent_email": "parent@example.com",
                "paid": True,
                "date": "21-10-2024",
                "time": "15:00"
            }
        ])

        # Create a mock blueprint
        self.mock_bp = Blueprint('teacher_bp', __name__)

        @self.mock_bp.route('/teacher_private_lessons')
        def teacher_private_lessons():
            teacher_email = session.get('email')
            if not teacher_email:
                return "User not logged in", 401

            lessons = self.db.private_lesson.find({'teacher_email': teacher_email, 'paid': True})
            return render_template_string("""
                <div>
                    {% for lesson in lessons %}
                        <p>{{ lesson.student_email }}</p>
                        <p>{{ lesson.date }} {{ lesson.time }}</p>
                    {% endfor %}
                </div>
            """, lessons=lessons)

        self.app.register_blueprint(self.mock_bp)

    def tearDown(self):
        self.mongo_client.drop_database("test_database")

    def test_private_lessons_display(self):
        with self.client.session_transaction() as sess:
            sess['email'] = 'teacher@example.com'

        response = self.client.get('/teacher_private_lessons')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'student1@example.com', response.data)
        self.assertIn(b'student2@example.com', response.data)

    def test_private_lessons_not_logged_in(self):
        response = self.client.get('/teacher_private_lessons')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'User not logged in', response.data)

if __name__ == '__main__':
    unittest.main()
