import unittest
from flask import Flask, Blueprint, session, request, jsonify
from app.modules.users.student.routes import student_bp
import mongomock
import os


# Mock utility functions
def generate_questions_mock(student_data, count):
    return [{
        'question': 'What is 2 + 2?',
        'possible_answers': ['3', '4', '5', '6'],
        'correct_answer': '4',
        'explanation': '2 + 2 equals 4.'
    }]

# Define mock endpoints for the missing routes
def mock_logout():
    return "Logout Page"

def mock_signup_form():
    return "Signup Form Page"

def mock_login_form():
    return "Login Form Page"

class StudentTestCase(unittest.TestCase):

    def setUp(self):
        print("Setting up Flask app for testing...")
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.secret_key = 'test_secret_key'  # Necessary for session management
        self.app.register_blueprint(student_bp, url_prefix='/student')
        
        # # Create a mock blueprint for the users_bp_main
        users_bp_main = Blueprint('users_bp_main', __name__)
        self.app.register_blueprint(users_bp_main, url_prefix='/users')

        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Connecting to the mock MongoDB
        print("Connecting to mock MongoDB...")
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client.get_database("test_database")
        self.db.questionnaire = self.db['questionnaire']
        self.db.childProcess = self.db['childProcess']

        # Mock the MongoDB object in routes
        student_bp.mongo = self.mongo_client
        student_bp.util = type('util', (), {'generate_questions': generate_questions_mock})

        # Adding mock student and questionnaire data
        print("Inserting test data...")
        self.db.questionnaire.insert_one({
            "student_email": "test@student.com",
            "parent_email": "parent@test.com",
            "full_name": "Test Student",
            "grade": "5th",
            "rating": "good",
            "first_subject": "math",
            "second_subject": "science"
        })
        self.db.childProcess.insert_one({
            "student_email": "test@student.com",
            "answers": []
        })

    def tearDown(self):
        # Dropping the test database
        print("Dropping test database...")
        self.mongo_client.drop_database("test_database")

    def test_submit_answer_correct(self):
        print("Testing submit answer endpoint with correct answer...")
        with self.client.session_transaction() as sess:
            sess['email'] = 'test@student.com'
        student_doc_bfore = self.db.childProcess.find_one({"student_email": "test@student.com"})
        response = self.client.post('/student/submit-answer', data={
            'answer': '4',
            'correctAnswer': '4',
            'explanation': '2 + 2 equals 4.'
        })
        student_doc_after = self.db.childProcess.find_one({"student_email": "test@student.com"})
        print(f"brfore: {student_doc_bfore}")
        print(student_doc_after)
        print(response.data)  # Print response for debugging
        self.assertEqual(response.status_code, 200, "Failed to submit answer")
        result = response.get_json()
        self.assertTrue(result['is_correct'], msg=f"result['is_correct']={result['is_correct']}")
        self.assertEqual(result['correct_answer'], '4', msg=f"result['correct_answer']={result['correct_answer']} != 4")
        self.assertEqual(result['explanation'], '2 + 2 equals 4.')

    def test_submit_answer_incorrect(self):
        print("Testing submit answer endpoint with incorrect answer...")
        with self.client.session_transaction() as sess:
            sess['email'] = 'test@student.com'
        response = self.client.post('/student/submit-answer', data={
            'answer': '3',
            'correctAnswer': '4',
            'explanation': '2 + 2 equals 4.'
        })
        print(response.data)  # Print response for debugging
        self.assertEqual(response.status_code, 200, "Failed to submit answer")
        result = response.get_json()
        self.assertFalse(result['is_correct'])
        self.assertEqual(result['correct_answer'], '4')
        self.assertEqual(result['explanation'], '2 + 2 equals 4.')

if __name__ == '__main__':
    unittest.main()

