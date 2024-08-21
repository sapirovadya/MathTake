import unittest
from flask import Flask, url_for, Blueprint
from app.modules.users.student.routes import student_bp
import mongomock
import os

def mock_logout():
    return "Logout Page"

def mock_signup_form():
    return "Signup Form Page"

def mock_login_form():
    return "Login Form Page"

def mock_fqa_page():
    return "Mocked FQA Page"

class QuestionnaireTestCase(unittest.TestCase):

    def setUp(self):
        # Creating a Flask app to test
        print("Setting up Flask app for testing...")
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.register_blueprint(student_bp, url_prefix='/student')
        
        # Registering mock routes
        self.app.add_url_rule('/logout', 'logout', mock_logout)
        
        # Create a mock blueprint for the users_bp_main
        users_bp_main = Blueprint('users_bp_main', __name__)
        users_bp_main.add_url_rule('/signup', 'signup_form', mock_signup_form)
        users_bp_main.add_url_rule('/login', 'login_form', mock_login_form)
        users_bp_main.add_url_rule('/FQA', 'FQA_page', mock_fqa_page)
        self.app.register_blueprint(users_bp_main, url_prefix='/users')

        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Connecting to the mock MongoDB
        print("Connecting to mock MongoDB...")
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client.get_database("test_database")
        self.db.students = self.db['students']
        self.db.questionnaire = self.db['questionnaire']

        # Mock the MongoDB object in routes
        student_bp.mongo = self.mongo_client

        # Adding mock student and questionnaire data
        print("Inserting test data...")
        self.db.students.insert_one({"name": "Test Student", "email": "test@student.com", "password": "test123"})
        self.db.questionnaire.insert_one({
            "student_email": "test@student.com",
            "parent_email": "parent@test.com",
            "full_name": "Test Student",
            "grade": "5th",
            "rating": "good",
            "first_subject": "math",
            "second_subject": "science"
        })

    def tearDown(self):
        # Dropping the test database
        print("Dropping test database...")
        self.mongo_client.drop_database("test_database")

    def test_questionnaire_display(self):
        print("Testing questionnaire display endpoint...")
        response = self.client.get('/student/questionnaire?email=test@student.com')
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200, "Failed to display questionnaire page")

    def test_submit_questionnaire(self):
        print("Testing submit questionnaire endpoint...")
        response = self.client.post('/student/submit_questionnaire', data={
            'email': 'test@student.com',
            'parent_email': 'parent@test.com',
            'fullName': 'Test Student',
            'grade': '6rd',
            'rating': 'good',
            'firstSubject': 'percentage',
            'secondSubject': 'division'
        })
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200, "Failed to submit questionnaire")

    def test_edit_questionnaire(self):
        print("Testing edit questionnaire endpoint...")
        response = self.client.get('/student/editquestionnaire/test@student.com/parent@test.com')
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200, "Failed to edit questionnaire")

    def test_update_questionnaire(self):
        print("Testing update questionnaire endpoint...")
        response = self.client.post('/student/updatequestionnaire', data={
            'email': 'test@student.com',
            'parent_email': 'parent@test.com',
            'fullName': 'Updated Test Student',
            'grade': '3rd',
            'rating': 'good',
            'firstSubject': 'division',
            'secondSubject': 'percentage'
        })
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200, "Failed to update questionnaire")

if __name__ == '__main__':
    unittest.main()

