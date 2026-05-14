// ===== Configuration =====
const API_BASE_URL = 'http://localhost:5002/api';

// ===== State Management =====
let todos = [];
let currentFilter = 'all';
let editingTodoId = null;
let deletingTodoId = null;

// ===== DOM Elements =====
const elements = {
    todoForm: document.getElementById('add-todo-form'),
    todoTitle: document.getElementById('todo-title'),
    todoDescription: document.getElementById('todo-description'),
    todoList: document.getElementById('todo-list'),
    loading: document.getElementById('loading'),
    errorMessage: document.getElementById('error-message'),
    errorText: document.getElementById('error-text'),
    emptyState: document.getElementById('empty-state'),
    filterTabs: document.querySelectorAll('.filter-tab'),
    toast: document.getElementById('toast'),
    toastMessage: document.getElementById('toast-message'),
    editModal: document.getElementById('edit-modal'),
    editForm: document.getElementById('edit-todo-form'),
    editTitle: document.getElementById('edit-title'),
    editDescription: document.getElementById('edit-description'),
    deleteModal: document.getElementById('delete-modal'),
    countAll: document.getElementById('count-all'),
    countActive: document.getElementById('count-active'),
    countCompleted: document.getElementById('count-completed'),
    countDeleted: document.getElementById('count-deleted'),
    totalStats: document.getElementById('total-stats')
};

// ===== API Functions =====
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'An error occurred');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function fetchTodos() {
    const includeDeleted = currentFilter === 'deleted';
    const endpoint = includeDeleted ? '/todos?include_deleted=true' : '/todos';
    const response = await apiRequest(endpoint);
    return response.data;
}

async function createTodo(title, description) {
    const response = await apiRequest('/todos', {
        method: 'POST',
        body: JSON.stringify({ title, description })
    });
    return response.data;
}

async function updateTodo(id, updates) {
    const response = await apiRequest(`/todos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(updates)
    });
    return response.data;
}

async function deleteTodo(id) {
    const response = await apiRequest(`/todos/${id}`, {
        method: 'DELETE'
    });
    return response.data;
}

async function restoreTodo(id) {
    const response = await apiRequest(`/todos/${id}/restore`, {
        method: 'POST'
    });
    return response.data;
}

async function permanentDeleteTodo(id) {
    const response = await apiRequest(`/todos/${id}/permanent`, {
        method: 'DELETE'
    });
    return response.data;
}

// ===== UI Functions =====
function showLoading() {
    elements.loading.classList.remove('hidden');
    elements.todoList.classList.add('hidden');
    elements.emptyState.classList.add('hidden');
    elements.errorMessage.classList.add('hidden');
}

function hideLoading() {
    elements.loading.classList.add('hidden');
}

function showError(message) {
    elements.errorText.textContent = message;
    elements.errorMessage.classList.remove('hidden');
    elements.todoList.classList.add('hidden');
    elements.emptyState.classList.add('hidden');
}

function showEmptyState() {
    elements.emptyState.classList.remove('hidden');
    elements.todoList.classList.add('hidden');
    elements.errorMessage.classList.add('hidden');
}

function showTodoList() {
    elements.todoList.classList.remove('hidden');
    elements.emptyState.classList.add('hidden');
    elements.errorMessage.classList.add('hidden');
}

function showToast(message, duration = 3000) {
    elements.toastMessage.textContent = message;
    elements.toast.classList.remove('hidden');
    
    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, duration);
}

function updateCounts() {
    const all = todos.filter(t => !t.deleted).length;
    const active = todos.filter(t => !t.completed && !t.deleted).length;
    const completed = todos.filter(t => t.completed && !t.deleted).length;
    const deleted = todos.filter(t => t.deleted).length;
    
    elements.countAll.textContent = all;
    elements.countActive.textContent = active;
    elements.countCompleted.textContent = completed;
    elements.countDeleted.textContent = deleted;
    
    const total = all + deleted;
    elements.totalStats.textContent = `${total} total task${total !== 1 ? 's' : ''}`;
}

function filterTodos() {
    switch (currentFilter) {
        case 'active':
            return todos.filter(t => !t.completed && !t.deleted);
        case 'completed':
            return todos.filter(t => t.completed && !t.deleted);
        case 'deleted':
            return todos.filter(t => t.deleted);
        default:
            return todos.filter(t => !t.deleted);
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 7) {
        return date.toLocaleDateString();
    } else if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (minutes > 0) {
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else {
        return 'Just now';
    }
}

function createTodoElement(todo) {
    const li = document.createElement('li');
    li.className = `todo-item ${todo.completed ? 'completed' : ''} ${todo.deleted ? 'deleted' : ''}`;
    li.dataset.id = todo.id;
    
    const isDeleted = todo.deleted;
    
    li.innerHTML = `
        <div class="todo-header">
            ${!isDeleted ? `
                <input 
                    type="checkbox" 
                    class="todo-checkbox" 
                    ${todo.completed ? 'checked' : ''}
                    onchange="toggleComplete(${todo.id})"
                >
            ` : ''}
            <div class="todo-content">
                <h3 class="todo-title">${escapeHtml(todo.title)}</h3>
                ${todo.description ? `<p class="todo-description">${escapeHtml(todo.description)}</p>` : ''}
                <div class="todo-meta">Created ${formatDate(todo.created_at)}</div>
            </div>
        </div>
        <div class="todo-actions">
            ${!isDeleted ? `
                <button class="todo-btn todo-btn-edit" onclick="openEditModal(${todo.id})">
                    ✏️ Edit
                </button>
                <button class="todo-btn todo-btn-delete" onclick="handleDelete(${todo.id})">
                    🗑️ Delete
                </button>
            ` : `
                <button class="todo-btn todo-btn-restore" onclick="handleRestore(${todo.id})">
                    ↩️ Restore
                </button>
                <button class="todo-btn todo-btn-delete" onclick="openDeleteModal(${todo.id})">
                    ❌ Delete Forever
                </button>
            `}
        </div>
    `;
    
    return li;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderTodos() {
    const filteredTodos = filterTodos();
    
    if (filteredTodos.length === 0) {
        showEmptyState();
        return;
    }
    
    showTodoList();
    elements.todoList.innerHTML = '';
    
    filteredTodos.forEach(todo => {
        const todoElement = createTodoElement(todo);
        elements.todoList.appendChild(todoElement);
    });
}

// ===== Event Handlers =====
async function handleAddTodo(e) {
    e.preventDefault();
    
    const title = elements.todoTitle.value.trim();
    const description = elements.todoDescription.value.trim();
    
    if (!title) {
        showToast('Please enter a title');
        return;
    }
    
    try {
        const newTodo = await createTodo(title, description);
        todos.unshift(newTodo);
        
        elements.todoForm.reset();
        renderTodos();
        updateCounts();
        showToast('Todo added successfully!');
    } catch (error) {
        showToast('Failed to add todo: ' + error.message);
    }
}

async function toggleComplete(id) {
    try {
        const todo = todos.find(t => t.id === id);
        if (!todo) return;
        
        const updatedTodo = await updateTodo(id, { completed: !todo.completed });
        
        const index = todos.findIndex(t => t.id === id);
        todos[index] = updatedTodo;
        
        renderTodos();
        updateCounts();
        showToast(updatedTodo.completed ? 'Todo completed!' : 'Todo marked as active');
    } catch (error) {
        showToast('Failed to update todo: ' + error.message);
        await loadTodos(); // Reload to sync state
    }
}

async function handleDelete(id) {
    try {
        await deleteTodo(id);
        
        const todo = todos.find(t => t.id === id);
        if (todo) {
            todo.deleted = true;
        }
        
        renderTodos();
        updateCounts();
        showToast('Todo moved to trash');
    } catch (error) {
        showToast('Failed to delete todo: ' + error.message);
    }
}

async function handleRestore(id) {
    try {
        const response = await restoreTodo(id);
        
        const todo = todos.find(t => t.id === id);
        if (todo) {
            todo.deleted = false;
        }
        
        renderTodos();
        updateCounts();
        showToast('Todo restored successfully!');
    } catch (error) {
        showToast('Failed to restore todo: ' + error.message);
    }
}

function handleFilterChange(filter) {
    currentFilter = filter;
    
    elements.filterTabs.forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.filter === filter) {
            tab.classList.add('active');
        }
    });
    
    renderTodos();
}

// ===== Modal Functions =====
function openEditModal(id) {
    const todo = todos.find(t => t.id === id);
    if (!todo) return;
    
    editingTodoId = id;
    elements.editTitle.value = todo.title;
    elements.editDescription.value = todo.description || '';
    elements.editModal.classList.remove('hidden');
}

function closeEditModal() {
    editingTodoId = null;
    elements.editModal.classList.add('hidden');
    elements.editForm.reset();
}

async function handleEditSubmit(e) {
    e.preventDefault();
    
    const title = elements.editTitle.value.trim();
    const description = elements.editDescription.value.trim();
    
    if (!title) {
        showToast('Please enter a title');
        return;
    }
    
    try {
        const updatedTodo = await updateTodo(editingTodoId, { title, description });
        
        const index = todos.findIndex(t => t.id === editingTodoId);
        todos[index] = updatedTodo;
        
        closeEditModal();
        renderTodos();
        showToast('Todo updated successfully!');
    } catch (error) {
        showToast('Failed to update todo: ' + error.message);
    }
}

function openDeleteModal(id) {
    deletingTodoId = id;
    elements.deleteModal.classList.remove('hidden');
}

function closeDeleteModal() {
    deletingTodoId = null;
    elements.deleteModal.classList.add('hidden');
}

async function confirmPermanentDelete() {
    if (!deletingTodoId) return;
    
    try {
        await permanentDeleteTodo(deletingTodoId);
        
        todos = todos.filter(t => t.id !== deletingTodoId);
        
        closeDeleteModal();
        renderTodos();
        updateCounts();
        showToast('Todo permanently deleted');
    } catch (error) {
        showToast('Failed to delete todo: ' + error.message);
    }
}

// ===== Load Todos =====
async function loadTodos() {
    showLoading();
    
    try {
        todos = await fetchTodos();
        hideLoading();
        renderTodos();
        updateCounts();
    } catch (error) {
        hideLoading();
        showError('Failed to load todos. Please check if the backend server is running.');
        console.error('Error loading todos:', error);
    }
}

// ===== Event Listeners =====
elements.todoForm.addEventListener('submit', handleAddTodo);
elements.editForm.addEventListener('submit', handleEditSubmit);

elements.filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        handleFilterChange(tab.dataset.filter);
    });
});

// Close modals when clicking outside
elements.editModal.addEventListener('click', (e) => {
    if (e.target === elements.editModal) {
        closeEditModal();
    }
});

elements.deleteModal.addEventListener('click', (e) => {
    if (e.target === elements.deleteModal) {
        closeDeleteModal();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape key closes modals
    if (e.key === 'Escape') {
        closeEditModal();
        closeDeleteModal();
    }
});

// ===== Make functions global for onclick handlers =====
window.toggleComplete = toggleComplete;
window.openEditModal = openEditModal;
window.closeEditModal = closeEditModal;
window.handleDelete = handleDelete;
window.handleRestore = handleRestore;
window.openDeleteModal = openDeleteModal;
window.closeDeleteModal = closeDeleteModal;
window.confirmPermanentDelete = confirmPermanentDelete;

// ===== Initialize App =====
document.addEventListener('DOMContentLoaded', () => {
    loadTodos();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadTodos();
    }, 30000);
});

// Made with Bob
