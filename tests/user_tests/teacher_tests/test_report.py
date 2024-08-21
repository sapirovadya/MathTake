import unittest
from flask import Flask, session, redirect, url_for
import mongomock
from app.modules.users.teacher.routes import teacher_bp
import os

class TeacherReportTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'supersecretkey'
        self.client = self.app.test_client()
        self.app.register_blueprint(teacher_bp)

        @self.app.route('/logout')
        def logout():
            return redirect(url_for('teacher_bp.student_report'))

        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client['test_database']
        self.db.private_lesson = self.db['private_lesson']
        self.db.reports = self.db['reports']

        self.db.private_lesson.insert_many([
            {
                "teacher_email": "teacher@example.com",
                "student_email": "student1@example.com",
                "paid": True,
                "date": "01-01-2024",
                "time": "10:00"
            },
            {
                "teacher_email": "teacher@example.com",
                "student_email": "student2@example.com",
                "paid": True,
                "date": "02-01-2024",
                "time": "11:00"
            }
        ])

        teacher_bp.mongo = self.mongo_client

    def tearDown(self):
        self.mongo_client.drop_database("test_database")

    def test_student_report_view(self):
        with self.client.session_transaction() as sess:
            sess['email'] = 'teacher@example.com'

        response = self.client.get('/student_report')
        self.assertEqual(response.status_code, 200)

    def test_submit_report_success(self):
        with self.client.session_transaction() as sess:
            sess['email'] = 'teacher@example.com'

        response = self.client.post('/submit_report', data={
            'student_email': 'student1@example.com',
            'report_content': 'Great progress!'
        })
        self.assertEqual(response.status_code, 302)  

if __name__ == '__main__':
    unittest.main()
