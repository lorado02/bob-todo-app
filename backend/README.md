# Todo App - Flask Backend

A RESTful API backend for a todo application built with Flask and SQLAlchemy.

## Features

- ✅ RESTful API with CRUD operations
- ✅ SQLite database with SQLAlchemy ORM
- ✅ CORS enabled for frontend integration
- ✅ Input validation and error handling
- ✅ Automatic timestamp management
- ✅ JSON response format

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **The API will be available at:**
   ```
   http://localhost:5001
   ```
   
   **Note for macOS users:** Port 5000 is used by AirPlay Receiver. The app uses port 5001 by default. To use port 5000, disable AirPlay Receiver in System Settings > General > AirPlay Receiver.

3. **The database will be automatically created** as `database.db` on first run.

## API Endpoints

### Base URL: `http://localhost:5001/api`

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/todos` | Get all todos | None |
| GET | `/todos/<id>` | Get single todo | None |
| POST | `/todos` | Create new todo | `{title, description?}` |
| PUT | `/todos/<id>` | Update todo | `{title?, description?, completed?}` |
| DELETE | `/todos/<id>` | Delete todo | None |
| GET | `/health` | Health check | None |

### Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## API Examples

### Get All Todos
```bash
curl http://localhost:5000/api/todos
```

### Create a Todo
```bash
curl -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

### Update a Todo
```bash
curl -X PUT http://localhost:5000/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete a Todo
```bash
curl -X DELETE http://localhost:5000/api/todos/1
```

## Project Structure

```
backend/
├── app.py              # Main Flask application with API routes
├── models.py           # SQLAlchemy Todo model
├── database.py         # Database configuration and initialization
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Database Schema

### Todo Model

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| title | String(200) | Todo title (required) |
| description | String(500) | Optional description |
| completed | Boolean | Completion status (default: False) |
| created_at | DateTime | Creation timestamp (auto-generated) |

## Development

### Running in Debug Mode

The application runs in debug mode by default when using `python app.py`. This enables:
- Auto-reload on code changes
- Detailed error messages
- Interactive debugger

### Database Management

The database is automatically created on first run. To reset the database:

1. Stop the Flask server
2. Delete `database.db`
3. Restart the server

### Testing the API

You can test the API using:
- **curl** (command line)
- **Postman** (GUI application)
- **Thunder Client** (VS Code extension)
- **Browser** (for GET requests)

## Troubleshooting

### Port Already in Use (macOS)
**Issue:** Port 5000 is used by AirPlay Receiver on macOS.

**Solution 1 (Recommended):** The app now uses port 5001 by default.

**Solution 2:** Disable AirPlay Receiver:
1. Open System Settings
2. Go to General > AirPlay Receiver
3. Turn off AirPlay Receiver

**Solution 3:** Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5002)
```

### Database Errors
If you encounter database errors:
1. Delete `database.db`
2. Restart the application
3. The database will be recreated automatically

### Import Errors
Make sure your virtual environment is activated and all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Dependencies

- **Flask 3.0.0** - Web framework
- **Flask-CORS 4.0.0** - Cross-Origin Resource Sharing
- **SQLAlchemy 2.0.23** - SQL toolkit and ORM

## License

This project is open source and available for educational purposes.

## Next Steps

After setting up the backend:
1. Test all API endpoints
2. Set up the frontend application
3. Connect frontend to backend API
4. Deploy to production (optional)