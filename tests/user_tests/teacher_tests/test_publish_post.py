import unittest
from flask import Flask, session, render_template_string, Blueprint, jsonify, request
from flask_session import Session
import mongomock
from datetime import datetime

class PostCreationTestCase(unittest.TestCase):
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
        self.db.posts = self.db['posts']

        # Insert mock posts
        self.db.posts.insert_many([
            {
                "writer_name": "Teacher One",
                "date": "20-10-2024",
                "content": "This is the first post."
            },
            {
                "writer_name": "Teacher Two",
                "date": "21-10-2024",
                "content": "This is the second post."
            }
        ])

        # Create a mock blueprint
        self.mock_bp = Blueprint('teacher_bp', __name__)

        @self.mock_bp.route('/posts')
        def view_posts():
            posts = self.db.posts.find()
            return render_template_string("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <title>Posts</title>
                    <meta content="width=device-width, initial-scale=1.0" name="viewport">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container-xxl py-5">
                        <div class="container">
                            <h1 class="mb-3">Posts</h1>
                            <form action="{{ url_for('teacher_bp.create_post') }}" method="post">
                                <div class="mb-3">
                                    <textarea class="form-control" id="post-content" name="post_content" rows="4"
                                        placeholder="Write your post here..."></textarea>
                                </div>
                                <button class="btn btn-primary mb-4" type="submit">Publish</button>
                            </form>

                            <!-- Display Posts -->
                            <div class="post-list">
                                {% for post in posts %}
                                <div class="post">
                                    <div class="post-header">
                                        <h5>{{ post.writer_name }}</h5> <small>{{ post.date }}</small>
                                    </div>
                                    <div class="post-content">
                                        <p>{{ post.content }}</p>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </body>
                </html>
            """, posts=posts)

        @self.mock_bp.route('/create_post', methods=['POST'])
        def create_post():
            post_content = request.form['post_content']
            writer_name = "Teacher Three"  # In a real scenario, this would come from the session or a similar source
            date = datetime.now().strftime("%d-%m-%Y")

            # Add the new post to the mock database
            self.db.posts.insert_one({
                "writer_name": writer_name,
                "date": date,
                "content": post_content
            })

            return jsonify(message="Post created successfully"), 200

        self.app.register_blueprint(self.mock_bp)

    def tearDown(self):
        self.mongo_client.drop_database("test_database")

    def test_post_creation(self):
        response = self.client.get('/posts')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Teacher One', response.data)
        self.assertIn(b'Teacher Two', response.data)

        # Simulate creating a new post via form submission
        response = self.client.post('/create_post', data={
            "post_content": "This is a new post."
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post created successfully', response.data)

        # Verify the new post was added to the database
        post = self.db.posts.find_one({"content": "This is a new post."})
        self.assertIsNotNone(post)
        self.assertEqual(post['writer_name'], "Teacher Three")

if __name__ == '__main__':
    unittest.main()