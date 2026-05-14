from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base


class Todo(Base):
    """Todo model representing a todo item in the database."""
    
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, title, description=None, completed=False):
        """Initialize a new Todo instance."""
        self.title = title
        self.description = description
        self.completed = completed
    
    def to_dict(self):
        """Convert Todo object to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of Todo object."""
        return f'<Todo {self.id}: {self.title}>'

# Made with Bob
