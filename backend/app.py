from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db_session, init_db, shutdown_session
from models import Todo

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Initialize database
with app.app_context():
    init_db()

# Register teardown function to close database session
@app.teardown_appcontext
def shutdown_session_on_teardown(exception=None):
    shutdown_session(exception)


# Helper function to create error response
def error_response(message, status_code=400):
    """Create a standardized error response."""
    return jsonify({
        'success': False,
        'error': message
    }), status_code


# Helper function to create success response
def success_response(data, status_code=200):
    """Create a standardized success response."""
    return jsonify({
        'success': True,
        'data': data
    }), status_code


# API Routes

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos."""
    try:
        todos = Todo.query.all()
        return success_response([todo.to_dict() for todo in todos])
    except Exception as e:
        return error_response(f'Failed to fetch todos: {str(e)}', 500)


@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a single todo by ID."""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return error_response('Todo not found', 404)
        return success_response(todo.to_dict())
    except Exception as e:
        return error_response(f'Failed to fetch todo: {str(e)}', 500)


@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'title' not in data:
            return error_response('Title is required', 400)
        
        if not data['title'].strip():
            return error_response('Title cannot be empty', 400)
        
        # Create new todo
        new_todo = Todo(
            title=data['title'].strip(),
            description=data.get('description', '').strip() if data.get('description') else None,
            completed=data.get('completed', False)
        )
        
        db_session.add(new_todo)
        db_session.commit()
        
        return success_response(new_todo.to_dict(), 201)
    except Exception as e:
        db_session.rollback()
        return error_response(f'Failed to create todo: {str(e)}', 500)


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update an existing todo."""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return error_response('Todo not found', 404)
        
        data = request.get_json()
        if not data:
            return error_response('No data provided', 400)
        
        # Update fields if provided
        if 'title' in data:
            if not data['title'].strip():
                return error_response('Title cannot be empty', 400)
            todo.title = data['title'].strip()
        
        if 'description' in data:
            todo.description = data['description'].strip() if data['description'] else None
        
        if 'completed' in data:
            todo.completed = bool(data['completed'])
        
        db_session.commit()
        
        return success_response(todo.to_dict())
    except Exception as e:
        db_session.rollback()
        return error_response(f'Failed to update todo: {str(e)}', 500)


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo."""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return error_response('Todo not found', 404)
        
        db_session.delete(todo)
        db_session.commit()
        
        return success_response({'message': 'Todo deleted successfully'})
    except Exception as e:
        db_session.rollback()
        return error_response(f'Failed to delete todo: {str(e)}', 500)


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return success_response({'status': 'healthy'})


# Root endpoint
@app.route('/')
def index():
    """Root endpoint with API information."""
    return jsonify({
        'message': 'Todo API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/todos': 'Get all todos',
            'GET /api/todos/<id>': 'Get a single todo',
            'POST /api/todos': 'Create a new todo',
            'PUT /api/todos/<id>': 'Update a todo',
            'DELETE /api/todos/<id>': 'Delete a todo',
            'GET /api/health': 'Health check'
        }
    })


if __name__ == '__main__':
    # Use port 5002 to avoid conflicts with macOS services (AirPlay on 5000, ControlCenter on 5001)
    app.run(debug=True, host='0.0.0.0', port=5002)

# Made with Bob
