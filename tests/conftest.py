import pytest
from app import create_app
from app.extensions import db
from dotenv import load_dotenv
import os

load_dotenv()


@pytest.fixture
def app():
    # Create the app using the loaded environment configuration
    os.environ["FLASK_ENV"] = "testing"
    app = create_app()

    with app.app_context():
        db.create_all()  # Create tables
        yield app  # Yield the app while the context is active
        db.session.remove()
        db.drop_all()  # Teardown: Clean up the database after each test


@pytest.fixture
def client(app):
    return app.test_client()  # Flask test client to send requests
