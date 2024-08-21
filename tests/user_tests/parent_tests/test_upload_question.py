import pytest
from unittest.mock import patch
from flask import Flask, session, request
from app.modules.users.parent.routes import select_child_uploadQ
from app.modules.users.parent.routes import upload_question
from app.modules.users.parent.routes import save_question

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret'
    return app

@patch('app.modules.users.parent.routes.render_template')
def test_upload_question(mock_render_template, app):
    with app.test_request_context('/upload_question?child_email=child@example.com'):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['email'] = 'parent@example.com'

            mock_render_template.return_value = 'rendered_template'

            response = upload_question()

            assert session['child_email'] == 'child@example.com'
            mock_render_template.assert_called_once_with('parent/upload_question.html', child_email='child@example.com')
            assert response == 'rendered_template'


import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from app.modules.users.parent.routes import select_child_uploadQ, save_question

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret'
    return app

@patch('app.modules.users.parent.routes.db')
@patch('app.modules.users.parent.routes.render_template')
def test_select_child_uploadQ(mock_render_template, mock_db, app):
    with app.test_request_context('/select_child_uploadQ'):
        mock_db.parents.find_one.return_value = {'students': ['child1@example.com', 'child2@example.com']}
        mock_render_template.return_value = 'rendered_template'

        # Inject mocks
        import app.modules.users.parent.routes as routes
        routes.db = mock_db
        routes.render_template = mock_render_template

        response = select_child_uploadQ()

    mock_db.parents.find_one.assert_called_once()
    mock_render_template.assert_called_once()
    assert response == 'rendered_template'






