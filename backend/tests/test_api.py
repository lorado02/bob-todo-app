import pytest
import json
from datetime import datetime
from models import Todo
from database import db_session


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test GET / returns API information."""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == 'Todo API'
        assert 'version' in data
        assert 'endpoints' in data


class TestHealthCheck:
    """Tests for the health check endpoint."""
    
    def test_health_check(self, client):
        """Test GET /api/health returns healthy status."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['status'] == 'healthy'


class TestGetTodos:
    """Tests for GET /api/todos endpoint."""
    
    def test_get_empty_todos(self, client):
        """Test getting todos when database is empty."""
        response = client.get('/api/todos')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []
    
    def test_get_todos_with_data(self, client, sample_todos):
        """Test getting todos when database has data."""
        response = client.get('/api/todos')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 3
        assert data['data'][0]['title'] == 'Todo 1'
    
    def test_get_todos_excludes_deleted(self, client, sample_todo, deleted_todo):
        """Test that deleted todos are excluded by default."""
        response = client.get('/api/todos')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['title'] == 'Test Todo'
    
    def test_get_todos_include_deleted(self, client, sample_todo, deleted_todo):
        """Test getting todos with include_deleted parameter."""
        response = client.get('/api/todos?include_deleted=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 2
        # Check that deleted field is included
        deleted_items = [t for t in data['data'] if t.get('deleted')]
        assert len(deleted_items) == 1


class TestGetSingleTodo:
    """Tests for GET /api/todos/<id> endpoint."""
    
    def test_get_existing_todo(self, client, sample_todo):
        """Test getting a single existing todo."""
        response = client.get(f'/api/todos/{sample_todo.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['id'] == sample_todo.id
        assert data['data']['title'] == 'Test Todo'
        assert data['data']['description'] == 'This is a test todo'
        assert data['data']['completed'] is False
    
    def test_get_nonexistent_todo(self, client):
        """Test getting a todo that doesn't exist."""
        response = client.get('/api/todos/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_get_deleted_todo(self, client, deleted_todo):
        """Test getting a deleted todo returns 410."""
        response = client.get(f'/api/todos/{deleted_todo.id}')
        assert response.status_code == 410
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'deleted' in data['error'].lower()


class TestCreateTodo:
    """Tests for POST /api/todos endpoint."""
    
    def test_create_todo_success(self, client):
        """Test creating a new todo successfully."""
        payload = {
            'title': 'New Todo',
            'description': 'A new test todo'
        }
        response = client.post('/api/todos',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == 'New Todo'
        assert data['data']['description'] == 'A new test todo'
        assert data['data']['completed'] is False
        assert 'id' in data['data']
    
    def test_create_todo_without_description(self, client):
        """Test creating a todo without description."""
        payload = {'title': 'Todo without description'}
        response = client.post('/api/todos',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == 'Todo without description'
        assert data['data']['description'] is None
    
    def test_create_todo_with_completed_flag(self, client):
        """Test creating a todo with completed flag."""
        payload = {
            'title': 'Completed Todo',
            'completed': True
        }
        response = client.post('/api/todos',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['completed'] is True
    
    def test_create_todo_missing_title(self, client):
        """Test creating a todo without title fails."""
        payload = {'description': 'No title'}
        response = client.post('/api/todos',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'title' in data['error'].lower()
    
    def test_create_todo_empty_title(self, client):
        """Test creating a todo with empty title fails."""
        payload = {'title': '   '}
        response = client.post('/api/todos',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'empty' in data['error'].lower()
    
    def test_create_todo_no_data(self, client):
        """Test creating a todo with no data fails."""
        response = client.post('/api/todos',
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestUpdateTodo:
    """Tests for PUT /api/todos/<id> endpoint."""
    
    def test_update_todo_title(self, client, sample_todo):
        """Test updating a todo's title."""
        payload = {'title': 'Updated Title'}
        response = client.put(f'/api/todos/{sample_todo.id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == 'Updated Title'
        assert data['data']['description'] == sample_todo.description
    
    def test_update_todo_description(self, client, sample_todo):
        """Test updating a todo's description."""
        payload = {'description': 'Updated description'}
        response = client.put(f'/api/todos/{sample_todo.id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['description'] == 'Updated description'
    
    def test_update_todo_completed(self, client, sample_todo):
        """Test updating a todo's completed status."""
        payload = {'completed': True}
        response = client.put(f'/api/todos/{sample_todo.id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['completed'] is True
    
    def test_update_todo_multiple_fields(self, client, sample_todo):
        """Test updating multiple fields at once."""
        payload = {
            'title': 'New Title',
            'description': 'New Description',
            'completed': True
        }
        response = client.put(f'/api/todos/{sample_todo.id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == 'New Title'
        assert data['data']['description'] == 'New Description'
        assert data['data']['completed'] is True
    
    def test_update_nonexistent_todo(self, client):
        """Test updating a todo that doesn't exist."""
        payload = {'title': 'Updated'}
        response = client.put('/api/todos/999',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_todo_empty_title(self, client, sample_todo):
        """Test updating with empty title fails."""
        payload = {'title': '   '}
        response = client.put(f'/api/todos/{sample_todo.id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'empty' in data['error'].lower()
    
    def test_update_todo_no_data(self, client, sample_todo):
        """Test updating with no data fails."""
        response = client.put(f'/api/todos/{sample_todo.id}',
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestDeleteTodo:
    """Tests for DELETE /api/todos/<id> endpoint (soft delete)."""
    
    def test_soft_delete_todo(self, client, sample_todo):
        """Test soft deleting a todo."""
        response = client.delete(f'/api/todos/{sample_todo.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'deleted successfully' in data['data']['message']
        
        # Verify todo is marked as deleted
        todo = Todo.query.get(sample_todo.id)
        assert todo is not None
        assert todo.deleted is True
        assert todo.deleted_at is not None
    
    def test_soft_delete_nonexistent_todo(self, client):
        """Test soft deleting a todo that doesn't exist."""
        response = client.delete('/api/todos/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_soft_delete_already_deleted_todo(self, client, deleted_todo):
        """Test soft deleting an already deleted todo."""
        response = client.delete(f'/api/todos/{deleted_todo.id}')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'already deleted' in data['error'].lower()


class TestRestoreTodo:
    """Tests for POST /api/todos/<id>/restore endpoint."""
    
    def test_restore_deleted_todo(self, client, deleted_todo):
        """Test restoring a deleted todo."""
        response = client.post(f'/api/todos/{deleted_todo.id}/restore')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'restored successfully' in data['data']['message']
        assert data['data']['todo']['id'] == deleted_todo.id
        
        # Verify todo is no longer deleted
        todo = Todo.query.get(deleted_todo.id)
        assert todo.deleted is False
        assert todo.deleted_at is None
    
    def test_restore_nonexistent_todo(self, client):
        """Test restoring a todo that doesn't exist."""
        response = client.post('/api/todos/999/restore')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_restore_non_deleted_todo(self, client, sample_todo):
        """Test restoring a todo that is not deleted."""
        response = client.post(f'/api/todos/{sample_todo.id}/restore')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not deleted' in data['error'].lower()


class TestGetDeletedTodos:
    """Tests for GET /api/todos/deleted endpoint."""
    
    def test_get_deleted_todos_empty(self, client, sample_todo):
        """Test getting deleted todos when none exist."""
        response = client.get('/api/todos/deleted')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []
    
    def test_get_deleted_todos_with_data(self, client, sample_todo, deleted_todo):
        """Test getting deleted todos when they exist."""
        response = client.get('/api/todos/deleted')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['id'] == deleted_todo.id
        assert data['data'][0]['deleted'] is True
        assert 'deleted_at' in data['data'][0]
    
    def test_get_deleted_todos_multiple(self, client, sample_todos):
        """Test getting multiple deleted todos."""
        # Delete two todos
        for todo in sample_todos[:2]:
            todo.deleted = True
            todo.deleted_at = datetime.utcnow()
        db_session.commit()
        
        response = client.get('/api/todos/deleted')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 2


class TestPermanentDelete:
    """Tests for DELETE /api/todos/<id>/permanent endpoint."""
    
    def test_permanent_delete_todo(self, client, sample_todo):
        """Test permanently deleting a todo."""
        todo_id = sample_todo.id
        response = client.delete(f'/api/todos/{todo_id}/permanent')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'permanently deleted' in data['data']['message']
        
        # Verify todo is completely removed
        todo = Todo.query.get(todo_id)
        assert todo is None
    
    def test_permanent_delete_deleted_todo(self, client, deleted_todo):
        """Test permanently deleting an already soft-deleted todo."""
        todo_id = deleted_todo.id
        response = client.delete(f'/api/todos/{todo_id}/permanent')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify todo is completely removed
        todo = Todo.query.get(todo_id)
        assert todo is None
    
    def test_permanent_delete_nonexistent_todo(self, client):
        """Test permanently deleting a todo that doesn't exist."""
        response = client.delete('/api/todos/999/permanent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_create_todo_with_whitespace_title(self, client):
        """Test creating a todo with whitespace in title (should be trimmed)."""
        payload = {'title': '  Whitespace Todo  '}
        response = client.post('/api/todos',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['data']['title'] == 'Whitespace Todo'
    
    def test_update_description_to_empty(self, client, sample_todo):
        """Test updating description to empty string."""
        payload = {'description': ''}
        response = client.put(f'/api/todos/{sample_todo.id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['description'] is None
    
    def test_create_todo_with_very_long_title(self, client):
        """Test creating a todo with a very long title."""
        long_title = 'A' * 200
        payload = {'title': long_title}
        response = client.post('/api/todos',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert len(data['data']['title']) == 200
    
    def test_invalid_json_payload(self, client):
        """Test sending invalid JSON."""
        response = client.post('/api/todos',
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code in [400, 500]
    
    def test_completed_field_type_conversion(self, client, sample_todo):
        """Test that completed field handles different truthy values."""
        # Test with string "true"
        payload = {'completed': 'true'}
        response = client.put(f'/api/todos/{sample_todo.id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['completed'] is True
        
        # Test with number 0
        payload = {'completed': 0}
        response = client.put(f'/api/todos/{sample_todo.id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['completed'] is False


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""
    
    def test_complete_todo_lifecycle(self, client):
        """Test complete lifecycle: create, update, complete, delete, restore."""
        # 1. Create a todo
        payload = {'title': 'Lifecycle Todo', 'description': 'Testing lifecycle'}
        response = client.post('/api/todos',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 201
        todo_id = json.loads(response.data)['data']['id']
        
        # 2. Update the todo
        payload = {'title': 'Updated Lifecycle Todo'}
        response = client.put(f'/api/todos/{todo_id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        
        # 3. Mark as completed
        payload = {'completed': True}
        response = client.put(f'/api/todos/{todo_id}',
                             data=json.dumps(payload),
                             content_type='application/json')
        assert response.status_code == 200
        
        # 4. Soft delete
        response = client.delete(f'/api/todos/{todo_id}')
        assert response.status_code == 200
        
        # 5. Verify it's in deleted list
        response = client.get('/api/todos/deleted')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']) == 1
        
        # 6. Restore
        response = client.post(f'/api/todos/{todo_id}/restore')
        assert response.status_code == 200
        
        # 7. Verify it's back in main list
        response = client.get('/api/todos')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']) == 1
        assert data['data'][0]['completed'] is True
    
    def test_multiple_todos_management(self, client):
        """Test managing multiple todos simultaneously."""
        # Create 5 todos
        todo_ids = []
        for i in range(5):
            payload = {'title': f'Todo {i+1}'}
            response = client.post('/api/todos',
                                  data=json.dumps(payload),
                                  content_type='application/json')
            todo_ids.append(json.loads(response.data)['data']['id'])
        
        # Delete 2 todos
        client.delete(f'/api/todos/{todo_ids[0]}')
        client.delete(f'/api/todos/{todo_ids[1]}')
        
        # Verify counts
        response = client.get('/api/todos')
        assert len(json.loads(response.data)['data']) == 3
        
        response = client.get('/api/todos/deleted')
        assert len(json.loads(response.data)['data']) == 2
        
        # Restore one
        client.post(f'/api/todos/{todo_ids[0]}/restore')
        
        # Verify new counts
        response = client.get('/api/todos')
        assert len(json.loads(response.data)['data']) == 4
        
        response = client.get('/api/todos/deleted')
        assert len(json.loads(response.data)['data']) == 1

# Made with Bob
