# Todo App - Frontend

A modern, responsive frontend for the Todo application built with vanilla JavaScript, HTML5, and CSS3.

## Features

- ✅ **Modern UI Design** - Clean, intuitive interface with gradient backgrounds
- ✅ **Responsive Layout** - Works seamlessly on desktop, tablet, and mobile
- ✅ **Real-time Updates** - Auto-refresh every 30 seconds
- ✅ **Filter Tabs** - View all, active, completed, or deleted todos
- ✅ **CRUD Operations** - Create, read, update, and delete todos
- ✅ **Soft Delete** - Move todos to trash before permanent deletion
- ✅ **Restore Functionality** - Recover deleted todos
- ✅ **Toast Notifications** - User-friendly feedback messages
- ✅ **Modal Dialogs** - Edit and delete confirmation modals
- ✅ **Dark Mode Support** - Automatic dark mode based on system preferences
- ✅ **Keyboard Shortcuts** - ESC to close modals
- ✅ **Loading States** - Visual feedback during API calls
- ✅ **Error Handling** - Graceful error messages

## Project Structure

```
frontend/
├── index.html          # Main HTML structure
├── css/
│   └── styles.css      # Responsive CSS styling (772 lines)
├── js/
│   └── app.js          # JavaScript application logic (509 lines)
├── assets/
│   └── (icons, images)
└── README.md           # This file
```

## Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with Flexbox/Grid
- **Vanilla JavaScript (ES6+)** - No frameworks or libraries
- **Fetch API** - HTTP requests to backend
- **CSS Variables** - Theming and customization
- **CSS Animations** - Smooth transitions and effects

## Setup Instructions

### Option 1: Open Directly in Browser

Simply open `index.html` in your web browser:

```bash
cd frontend
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or
start index.html  # Windows
```

### Option 2: Use a Local Server (Recommended)

Using a local server prevents CORS issues and provides a better development experience:

**Python 3:**
```bash
cd frontend
python -m http.server 8000
```

**Python 2:**
```bash
cd frontend
python -m SimpleHTTPServer 8000
```

**Node.js (http-server):**
```bash
npm install -g http-server
cd frontend
http-server -p 8000
```

**VS Code Live Server:**
1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

Then visit: `http://localhost:8000`

## Configuration

### API Endpoint

The frontend connects to the backend API at `http://localhost:5002/api` by default.

To change the API endpoint, edit `js/app.js`:

```javascript
const API_BASE_URL = 'http://localhost:5002/api';
```

### Auto-refresh Interval

Todos are automatically refreshed every 30 seconds. To change this, edit `js/app.js`:

```javascript
// Change 30000 (30 seconds) to your preferred interval in milliseconds
setInterval(() => {
    loadTodos();
}, 30000);
```

## Usage Guide

### Adding a Todo

1. Enter a title in the "What needs to be done?" field
2. Optionally add a description
3. Click "Add Todo" or press Enter

### Completing a Todo

- Click the checkbox next to a todo to mark it as complete
- Click again to mark as incomplete

### Editing a Todo

1. Click the "✏️ Edit" button on a todo
2. Modify the title and/or description
3. Click "Save Changes"

### Deleting a Todo

1. Click the "🗑️ Delete" button
2. The todo moves to the "Deleted" tab
3. You can restore it from there

### Permanently Deleting a Todo

1. Go to the "Deleted" tab
2. Click "❌ Delete Forever"
3. Confirm the deletion
4. **Warning:** This action cannot be undone

### Restoring a Deleted Todo

1. Go to the "Deleted" tab
2. Click "↩️ Restore" on the todo
3. The todo returns to your active list

### Filtering Todos

Use the filter tabs to view:
- **All** - All active todos
- **Active** - Incomplete todos
- **Completed** - Completed todos
- **Deleted** - Deleted todos (trash)

## Features in Detail

### Responsive Design

The app adapts to different screen sizes:

- **Desktop (>768px)** - Full layout with side-by-side elements
- **Tablet (768px)** - Adjusted spacing and font sizes
- **Mobile (<480px)** - Stacked layout, full-width buttons

### Dark Mode

The app automatically switches to dark mode based on your system preferences. No manual toggle needed.

### Toast Notifications

Toast messages appear in the bottom-right corner for:
- Todo added
- Todo updated
- Todo deleted
- Todo restored
- Error messages

### Loading States

Visual feedback is provided during:
- Initial page load
- API requests
- Data updates

### Error Handling

The app gracefully handles:
- Network errors
- API errors
- Invalid input
- Backend unavailability

## Keyboard Shortcuts

- **ESC** - Close open modals
- **Enter** - Submit forms

## Browser Compatibility

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Performance

- **Initial Load** - < 1 second
- **Todo Rendering** - Instant
- **API Calls** - < 500ms (local)
- **Animations** - 60 FPS

## Accessibility

- Semantic HTML5 elements
- Proper form labels
- Keyboard navigation support
- Focus indicators
- ARIA attributes (where needed)

## Customization

### Colors

Edit CSS variables in `css/styles.css`:

```css
:root {
    --primary-color: #4f46e5;  /* Change primary color */
    --success-color: #10b981;  /* Change success color */
    --danger-color: #ef4444;   /* Change danger color */
}
```

### Fonts

Change the font family in `css/styles.css`:

```css
body {
    font-family: 'Your Font', sans-serif;
}
```

### Layout

Adjust the container width in `css/styles.css`:

```css
.container {
    max-width: 800px;  /* Change to your preferred width */
}
```

## Troubleshooting

### Issue: Todos not loading

**Solution:**
1. Check if the backend server is running on port 5002
2. Open browser console (F12) to see error messages
3. Verify the API_BASE_URL in `js/app.js`

### Issue: CORS errors

**Solution:**
1. Make sure Flask-CORS is installed in the backend
2. Use a local server instead of opening HTML directly
3. Check backend CORS configuration

### Issue: Styles not loading

**Solution:**
1. Check that `css/styles.css` exists
2. Verify the path in `index.html`
3. Clear browser cache (Ctrl+Shift+R)

### Issue: JavaScript not working

**Solution:**
1. Check that `js/app.js` exists
2. Open browser console for error messages
3. Ensure JavaScript is enabled in your browser

## Development

### File Organization

- **index.html** - Structure and layout
- **css/styles.css** - All styling and responsive design
- **js/app.js** - Application logic and API calls

### Code Structure

The JavaScript is organized into sections:
1. Configuration
2. State Management
3. DOM Elements
4. API Functions
5. UI Functions
6. Event Handlers
7. Modal Functions
8. Initialization

### Adding New Features

1. Add HTML structure in `index.html`
2. Add styles in `css/styles.css`
3. Add logic in `js/app.js`
4. Test on multiple screen sizes

## API Integration

The frontend communicates with the backend using these endpoints:

- `GET /api/todos` - Fetch all todos
- `GET /api/todos?include_deleted=true` - Fetch all including deleted
- `POST /api/todos` - Create new todo
- `PUT /api/todos/:id` - Update todo
- `DELETE /api/todos/:id` - Soft delete todo
- `POST /api/todos/:id/restore` - Restore deleted todo
- `DELETE /api/todos/:id/permanent` - Permanently delete todo

## Future Enhancements

Potential improvements:
- [ ] Drag and drop reordering
- [ ] Due dates and reminders
- [ ] Categories/tags
- [ ] Search functionality
- [ ] Bulk operations
- [ ] Export to CSV/JSON
- [ ] Offline support (Service Worker)
- [ ] User authentication
- [ ] Dark mode toggle
- [ ] Custom themes

## Contributing

To contribute:
1. Test your changes on multiple browsers
2. Ensure responsive design works
3. Follow existing code style
4. Add comments for complex logic

## License

This project is open source and available for educational purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Verify backend is running
4. Check API endpoint configuration

## Credits

Built with ❤️ using vanilla JavaScript, HTML5, and CSS3.