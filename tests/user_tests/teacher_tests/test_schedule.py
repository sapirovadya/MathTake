import unittest
from flask import Flask, session, render_template_string, Blueprint, jsonify, request
from flask_session import Session
import mongomock

class TeacherSchedulingTestCase(unittest.TestCase):
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
                "student_email": "student1@example.com",
                "date": "20-10-2024",
                "time": "14:00"
            },
            {
                "teacher_email": "teacher@example.com",
                "student_email": "student2@example.com",
                "date": "21-10-2024",
                "time": "15:00"
            }
        ])

        # Create a mock blueprint
        self.mock_bp = Blueprint('teacher_bp', __name__)

        @self.mock_bp.route('/scheduling')
        def scheduling():
            lessons = self.db.lessons.find({'teacher_email': 'teacher@example.com'})
            return render_template_string("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <title>MathTake</title>
                    <meta content="width=device-width, initial-scale=1.0" name="viewport">
                    <meta content="" name="keywords">
                    <meta content="" name="description">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container py-5">
                        <div class="row g-4">
                            {% for lesson in lessons %}
                            <div class="col-lg-4 col-md-6">
                                <div class="lesson-item bg-light rounded p-4">
                                    <p><strong>Student Email:</strong> {{ lesson.student_email }}</p>
                                    <button class="btn btn-primary btn-set-time" data-email="{{ lesson.student_email }}">Set Time</button>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    <div class="modal fade" id="scheduleModal" tabindex="-1" aria-labelledby="scheduleModalLabel" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="scheduleModalLabel">Set Time</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <form id="scheduleForm">
                                        <div class="mb-3">
                                            <label for="datetime" class="form-label">Enter Date</label>
                                            <input type="text" id="datetime" class="form-control" placeholder="e.g., 23-07-2024" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="time" class="form-label">Enter Time</label>
                                            <input type="text" id="time" class="form-control" placeholder="e.g., 14:30" required>
                                        </div>
                                        <input type="hidden" id="studentEmail">
                                        <button type="submit" class="btn btn-primary" id="submitBtn">Schedule</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
            """, lessons=lessons)

        @self.mock_bp.route('/scheduleLesson', methods=['POST'])
        def schedule_lesson():
            data = request.get_json()
            student_email = data.get('student_email')
            date = data.get('date')
            time = data.get('time')

            # Add the new lesson to the mock database
            self.db.lessons.insert_one({
                "teacher_email": "teacher@example.com",
                "student_email": student_email,
                "date": date,
                "time": time
            })

            return jsonify(message="Lesson scheduled successfully"), 200

        self.app.register_blueprint(self.mock_bp)

    def tearDown(self):
        self.mongo_client.drop_database("test_database")

    def test_lesson_scheduling(self):
        response = self.client.get('/scheduling')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'student1@example.com', response.data)
        self.assertIn(b'student2@example.com', response.data)

        # Simulate scheduling a lesson via AJAX
        response = self.client.post('/scheduleLesson', json={
            "student_email": "student3@example.com",
            "date": "22-10-2024",
            "time": "16:00"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Lesson scheduled successfully', response.data)

        # Verify the new lesson was added to the database
        lesson = self.db.lessons.find_one({"student_email": "student3@example.com"})
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson['date'], "22-10-2024")
        self.assertEqual(lesson['time'], "16:00")

if __name__ == '__main__':
    unittest.main()
