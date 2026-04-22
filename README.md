# TaskFlow — Full Stack Task Management App
### Professional SaaS Dashboard | Flask + SQLite + JWT + Vanilla JS

---

## 📁 Project Structure

```
taskflow/
├── backend/
│   ├── app.py              ← Flask REST API
│   └── requirements.txt    ← Python dependencies
├── frontend/
│   └── index.html          ← Complete SPA (HTML + CSS + JS)
└── README.md
```

---

## ⚡ Quick Start (Demo Mode)

Open `frontend/index.html` directly in any browser → click **"Try Demo"** to start instantly with sample data. No backend needed.

---

## 🖥️ Backend Setup (Full Stack Mode)

### Prerequisites
- Python 3.9+
- pip

### Step 1 — Create Virtual Environment
```bash
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Environment Variables (optional)
```bash
# Create .env file
SECRET_KEY=your_super_secret_key_here
PORT=5000
FLASK_ENV=development
DB_PATH=taskflow.db
```

### Step 4 — Run the Server
```bash
python app.py
```
Output:
```
✅ Database initialized
🚀 TaskFlow API running on http://localhost:5000
```

### Step 5 — Connect Frontend to Backend
1. Open `frontend/index.html` in browser
2. Go to **Settings** (sidebar)
3. Under "Backend Connection", enter: `http://localhost:5000`
4. Click **Connect to Backend**
5. You should see ✅ Connected

---

## 🔐 Authentication Flow

```
User → POST /register → JWT Token returned
User → POST /login    → JWT Token returned
All protected routes  → Header: Authorization: Bearer <token>
```

---

## 📡 REST API Reference

### Base URL
```
http://localhost:5000
```

---

### `GET /health`
**Health Check** — No auth required

**Response:**
```json
{
  "status": "healthy",
  "service": "TaskFlow API",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### `POST /register`
**Register a new user** — No auth required

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "secret123"
}
```

**Success Response (201):**
```json
{
  "message": "Registration successful",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com"
  }
}
```

**Error (409 - Email exists):**
```json
{ "error": "Email already registered" }
```

---

### `POST /login`
**Login existing user** — No auth required

**Request Body:**
```json
{
  "email": "jane@example.com",
  "password": "secret123"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com"
  }
}
```

**Error (401):**
```json
{ "error": "Invalid email or password" }
```

---

### `GET /me`
**Get current user** — Auth required

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response:**
```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "created_at": "2024-01-15 10:30:00"
}
```

---

### `GET /tasks`
**Get all tasks with analytics** — Auth required

**Query Parameters (all optional):**
```
?status=pending|completed|in_progress
?priority=high|medium|low
?search=keyword
```

**Example:** `GET /tasks?status=pending&priority=high`

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Design landing page",
      "description": "Create wireframes and mockups",
      "status": "pending",
      "priority": "high",
      "due_date": "2024-01-20",
      "position": 0,
      "created_at": "2024-01-15 10:00:00",
      "updated_at": "2024-01-15 10:00:00"
    }
  ],
  "analytics": {
    "total": 8,
    "completed": 3,
    "pending": 4,
    "high_priority": 2,
    "productivity": 37.5
  }
}
```

---

### `POST /tasks`
**Create a new task** — Auth required

**Request Body:**
```json
{
  "title": "Fix login bug",
  "description": "Bug on iOS Safari login",
  "priority": "high",
  "status": "pending",
  "due_date": "2024-01-20"
}
```

**Required:** `title`
**Optional:** `description`, `priority` (low/medium/high), `status`, `due_date`

**Success Response (201):**
```json
{
  "message": "Task created",
  "task": {
    "id": 9,
    "title": "Fix login bug",
    "status": "pending",
    "priority": "high",
    ...
  }
}
```

---

### `PUT /tasks/:id`
**Update a task** — Auth required

**Request Body (all fields optional):**
```json
{
  "title": "Fix login bug - urgent",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2024-01-18"
}
```

**Success Response (200):**
```json
{
  "message": "Task updated",
  "task": { ... }
}
```

**Error (404):**
```json
{ "error": "Task not found" }
```

---

### `DELETE /tasks/:id`
**Delete a task** — Auth required

**Success Response (200):**
```json
{ "message": "Task deleted" }
```

---

### `PUT /tasks/reorder`
**Reorder tasks (drag & drop)** — Auth required

**Request Body:**
```json
{
  "order": [
    { "id": 3, "position": 0 },
    { "id": 1, "position": 1 },
    { "id": 5, "position": 2 }
  ]
}
```

---

## 🧪 Postman Testing Guide

### Step 1 — Set Up Environment
In Postman, create an environment with:
```
base_url  =  http://localhost:5000
token     =  (empty, will be set automatically)
```

### Step 2 — Register
```
POST {{base_url}}/register
Body (JSON):
{
  "name": "Test User",
  "email": "test@example.com",
  "password": "test123"
}
```
Copy the token from response → set as `token` in environment.

### Step 3 — Login
```
POST {{base_url}}/login
Body (JSON):
{
  "email": "test@example.com",
  "password": "test123"
}
```

### Step 4 — Add Auth Header to all protected requests
```
Authorization: Bearer {{token}}
```

### Step 5 — Create Task
```
POST {{base_url}}/tasks
Headers: Authorization: Bearer {{token}}
Body (JSON):
{
  "title": "My first task",
  "description": "Created via Postman",
  "priority": "high",
  "due_date": "2024-12-31"
}
```

### Step 6 — Get All Tasks
```
GET {{base_url}}/tasks
Headers: Authorization: Bearer {{token}}
```

### Step 7 — Update Task (replace 1 with your task id)
```
PUT {{base_url}}/tasks/1
Headers: Authorization: Bearer {{token}}
Body (JSON):
{
  "status": "completed"
}
```

### Step 8 — Delete Task
```
DELETE {{base_url}}/tasks/1
Headers: Authorization: Bearer {{token}}
```

### Postman Collection Import
You can also create a Postman collection JSON file with all these requests pre-configured.

---

## 🚀 Deployment Guide

### Backend → Render.com (Free)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your repository
4. Configure:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
   Environment Variables:
     SECRET_KEY = your_production_secret_key
     FLASK_ENV  = production
   ```
5. Click "Create Web Service"
6. Your API URL will be: `https://your-app.onrender.com`

### Backend → Railway.app

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Add environment variables (SECRET_KEY, PORT)
3. Railway auto-detects Python and runs the app
4. Copy the generated URL

### Frontend → Netlify (Free)

1. Go to [netlify.com](https://netlify.com) → Add new site → Deploy manually
2. Drag & drop the `frontend/` folder
3. Your site is live instantly!
4. Go to Settings → Open the app → Settings tab
5. Enter your backend URL and click "Connect to Backend"

### Frontend → Vercel

```bash
npm i -g vercel
cd frontend
vercel
```

### Frontend → GitHub Pages

1. Push the `frontend/` folder to a GitHub repo
2. Go to Settings → Pages → Source: main branch
3. Your site: `https://username.github.io/repo-name/`

---

## 🗄️ Database Schema

```sql
CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    avatar     TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT DEFAULT '',
    status      TEXT DEFAULT 'pending',    -- pending | in_progress | completed
    priority    TEXT DEFAULT 'medium',     -- low | medium | high
    due_date    TEXT DEFAULT NULL,
    position    INTEGER DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## ✨ Features Summary

| Feature | Status |
|---------|--------|
| JWT Authentication (register/login/logout) | ✅ |
| Full CRUD for tasks | ✅ |
| Demo mode (works without backend) | ✅ |
| Task priority (High/Medium/Low) | ✅ |
| Task status (Pending/In Progress/Done) | ✅ |
| Due dates with overdue highlighting | ✅ |
| Analytics dashboard with animated counters | ✅ |
| Progress bars | ✅ |
| Dark/Light mode toggle | ✅ |
| Drag & drop task reordering | ✅ |
| Search tasks | ✅ |
| Filter by status & priority | ✅ |
| Sort (newest, oldest, due date, priority) | ✅ |
| Deadline notifications/alerts | ✅ |
| Responsive (mobile + desktop) | ✅ |
| Sidebar navigation | ✅ |
| Toast notifications | ✅ |
| Keyboard shortcuts (Ctrl+N, Ctrl+K, Esc) | ✅ |
| Settings panel | ✅ |
| SQLite persistence | ✅ |
| LocalStorage fallback | ✅ |
| CORS enabled | ✅ |
| Gunicorn production server | ✅ |

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + N` | Open Add Task modal |
| `Ctrl + K` | Focus search bar |
| `Esc`      | Close modal |

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3 (custom design system), Vanilla JS |
| Backend | Python 3, Flask, Flask-CORS |
| Database | SQLite (via Python stdlib) |
| Auth | JWT (PyJWT), bcrypt |
| Fonts | Syne (display), DM Sans (body) |
| Icons | Font Awesome 6 |
| Deployment | Render/Railway (backend), Netlify/Vercel (frontend) |
