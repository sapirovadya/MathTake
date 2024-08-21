import unittest
from flask import Flask, render_template_string, Blueprint
from flask_session import Session
import mongomock
from datetime import datetime

class LessonSummaryTestCase(unittest.TestCase):
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
        self.db.lessons = self.db['lessons']

        # Insert mock lessons
        self.db.lessons.insert_many([
            {
                "teacher_email": "teacher@example.com",
                "lesson_date": "10-08-2024"
            },
            {
                "teacher_email": "teacher@example.com",
                "lesson_date": "15-08-2024"
            }
        ])

        # Create a mock blueprint
        self.mock_bp = Blueprint('teacher_bp', __name__)

        @self.mock_bp.route('/view_salary')
        def view_salary():
            num_lessons = self.db.lessons.count_documents({"teacher_email": "teacher@example.com"})
            lesson_rate = 90
            total_earnings = num_lessons * lesson_rate
            return render_template_string("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <title>Salary</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container-xxl py-5">
                        <div class="container">
                            <h1 class="mb-3">Salary</h1>
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>The number of lessons that took place</th>
                                        <th>The rate of the lesson (NIS)</th>
                                        <th>Total Earnings (NIS)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>{{ num_lessons }}</td>
                                        <td>{{ lesson_rate }}</td>
                                        <td>{{ total_earnings }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </body>
                </html>
            """, num_lessons=num_lessons, lesson_rate=lesson_rate, total_earnings=total_earnings)

        self.app.register_blueprint(self.mock_bp)

    def tearDown(self):
        self.mongo_client.drop_database("test_database")

    def test_view_salary(self):
        response = self.client.get('/view_salary')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'2', response.data)  # Number of lessons
        self.assertIn(b'90', response.data)  # Lesson rate
        self.assertIn(b'180', response.data)  # Total earnings

if __name__ == '_main_':
   unittest.main()
