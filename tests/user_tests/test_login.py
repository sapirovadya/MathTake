import unittest
from flask import Flask
from app.modules.users.routes import users_bp_main
import mongomock
import os

class LoginTestCase(unittest.TestCase):

    def setUp(self):
        # creating a Flask app to test
        print("Setting up Flask app for testing...")
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.register_blueprint(users_bp_main)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # connecting to the base of MongoDB using mongomock
        print("Connecting to mock MongoDB...")
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client.get_database("test_database")
        self.db.parents = self.db['parents']
        self.db.teachers = self.db['teachers']
        self.db.students = self.db['students']

        # Mock the mongo object in routes
        users_bp_main.mongo = self.mongo_client

        # adding users
        print("Inserting test users...")
        self.db.parents.insert_one({"name": "Parent User", "email": "parent@example.com", "password": "password123", "role": "Parent"})
        self.db.teachers.insert_one({"name": "Teacher User", "email": "teacher@example.com", "password": "password124", "role": "Teacher"})
        self.db.students.insert_one({"name": "Student User", "email": "student@example.com", "password": "password125", "role": "Student"})

    def tearDown(self):
        # delete the db after running the test
        print("Dropping test database...")
        self.mongo_client.drop_database("test_database")

    def test_teacher_login_success(self):
        print("Testing teacher login...")
        response = self.client.post('/login', data={"email": "teacher@example.com", "password": "password123"})
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200, "Failed to login as Teacher")  

    def test_parent_login_success(self):
        print("Testing parent login...")
        response = self.client.post('/login', data={"email": "parent@example.com", "password": "password124"})
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200, "Failed to login as Parent") 

    def test_student_login_success(self):
        print("Testing student login...")
        response = self.client.post('/login', data={"email": "student@example.com", "password": "password125"})
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200, "Failed to login as Student")  

if __name__ == '__main__':
    unittest.main()
