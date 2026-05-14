import pytest
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from database import Base, engine, db_session
from models import Todo


@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    # Set testing configuration
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield flask_app
    
    # Cleanup
    db_session.remove()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def sample_todo():
    """Create a sample todo for testing."""
    todo = Todo(
        title="Test Todo",
        description="This is a test todo",
        completed=False
    )
    db_session.add(todo)
    db_session.commit()
    return todo


@pytest.fixture(scope='function')
def sample_todos():
    """Create multiple sample todos for testing."""
    todos = [
        Todo(title="Todo 1", description="First todo", completed=False),
        Todo(title="Todo 2", description="Second todo", completed=True),
        Todo(title="Todo 3", description="Third todo", completed=False),
    ]
    for todo in todos:
        db_session.add(todo)
    db_session.commit()
    return todos


@pytest.fixture(scope='function')
def deleted_todo():
    """Create a deleted todo for testing restore functionality."""
    from datetime import datetime
    todo = Todo(
        title="Deleted Todo",
        description="This todo is deleted",
        completed=False
    )
    todo.deleted = True
    todo.deleted_at = datetime.utcnow()
    db_session.add(todo)
    db_session.commit()
    return todo

# Made with Bob
