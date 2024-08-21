import unittest
from flask import Flask, session, jsonify, Blueprint
from bson.objectid import ObjectId
import mongomock
import os
from flask_session import Session

class PaymentTestCase(unittest.TestCase):

    def setUp(self):
        # Set up Flask app for testing
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.config['TESTING'] = True
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SECRET_KEY'] = 'supersecretkey'
        Session(self.app)
        self.client = self.app.test_client()

        # Connect to mock MongoDB
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client.get_database("test_database")
        self.db.private_lesson = self.db['private_lesson']
        self.db.parents = self.db['parents']

        # Insert test data
        self.db.parents.insert_one({"email": "parent@example.com", "password": "password123"})
        lesson_id = self.db.private_lesson.insert_one({
            "teacher_email": "teacher@example.com",
            "student_email": "student@example.com",
            "parent_email": "parent@example.com",
            "paid": False,
            "date": "20-10-2024",
            "time": "14:00"
        }).inserted_id
        self.lesson_id = str(lesson_id)

        # Create a mock blueprint for testing
        self.mock_bp = Blueprint('mock_bp', __name__)

        @self.mock_bp.route("/process_payment/<lesson_id>", methods=['POST'])
        def process_payment(lesson_id):
            parent_email = session.get('email')
            if not parent_email:
                return jsonify({'success': False, 'message': 'User not logged in'}), 401

            lesson = self.db.private_lesson.find_one({'_id': ObjectId(lesson_id), 'parent_email': parent_email})
            if not lesson:
                return jsonify({'success': False, 'message': 'Lesson not found'}), 404

            self.db.private_lesson.update_one({'_id': ObjectId(lesson_id)}, {'$set': {'paid': True}})
            return jsonify({'success': True, 'message': 'Payment processed successfully'})

        self.app.register_blueprint(self.mock_bp)

    def tearDown(self):
        self.mongo_client.drop_database("test_database")

    def test_payment_process(self):
        with self.client:
            # Set session data directly in the test context
            with self.client.session_transaction() as sess:
                sess['email'] = 'parent@example.com'

            # Perform the payment process
            response = self.client.post(f'/process_payment/{self.lesson_id}')
            self.assertEqual(response.status_code, 200)  # Ensure the response is OK

            # Debug prints
            print(f"Response status code: {response.status_code}")
            updated_lesson = self.db.private_lesson.find_one({"_id": ObjectId(self.lesson_id)})
            print(f"Updated lesson: {updated_lesson}")

            # Check if the 'paid' field is updated in the lesson
            self.assertTrue(updated_lesson['paid'])

if __name__ == '__main__':
    unittest.main()
