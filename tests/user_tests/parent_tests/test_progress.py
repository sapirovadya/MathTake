import unittest
from flask import Flask
from flask import Blueprint
from app.modules.users.parent.routes import parent_bp
import mongomock
import os

def mock_fqa_page():
    return "Mocked FQA Page"
def mock_logout():
    return "Logged out"

class ParentTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.secret_key = 'test_secret_key'
        self.app.register_blueprint(parent_bp, url_prefix='/parent')
        users_bp_main = Blueprint('users_bp_main', __name__)
        users_bp_main.add_url_rule('/FQA', 'FQA_page', mock_fqa_page)
        users_bp_main.add_url_rule('/logout', 'logout', mock_logout)  
        self.app.register_blueprint(users_bp_main, url_prefix='/users')

        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client.db
        parent_bp.db = self.db

        with self.app.app_context():
            # Add mock data
            self.db.parents.insert_one({
                "email": "parent@test.com",
                "students": ["student1@test.com", "student2@test.com"]
            })
            self.db.childProcess.insert_one({
                "student_email": "student1@test.com",
                "answers": [{"date": "2024-08-01", "correct": 3, "incorrect": 1}]
            })
            self.db.testsEval.insert_one({
                "student_email": "student1@test.com",
                "answers": [{"date": "2024-08-01", "correct": 2, "incorrect": 2}]
            })

    def test_show_progress_no_child_email(self):
        response = self.client.get('/parent/show_progress')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/parent/select_child', response.location)


if __name__ == '__main__':
    unittest.main()
