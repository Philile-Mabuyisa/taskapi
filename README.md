# TaskAPI

A personal task manager REST API built with Python and FastAPI.

## What it does

Users can register, log in, and manage their personal tasks. Every task has a title, status, priority, and optional due date. All routes are protected — you can only see your own tasks.

## Tech stack

| Tool | Why |
|------|-----|
| FastAPI | Modern Python web framework — auto-generates docs |
| SQLite + SQLAlchemy | Database + ORM — no server setup needed |
| JWT (python-jose) | Secure stateless authentication |
| bcrypt (passlib) | Password hashing — never store plain text |
| Pytest | Automated tests |

## Project structure

```
taskapi/
├── main.py               # App entry point
├── requirements.txt      # Dependencies
├── .env                  # Secret keys (not committed to git)
├── app/
│   ├── database.py       # DB connection and session
│   ├── models/
│   │   └── models.py     # Database tables (User, Task)
│   ├── schemas/
│   │   └── schemas.py    # Request/response shapes (Pydantic)
│   ├── core/
│   │   └── auth.py       # Password hashing + JWT logic
│   └── routers/
│       ├── auth.py       # /auth/register, /auth/login
│       └── tasks.py      # /tasks CRUD endpoints
└── tests/
    └── test_tasks.py     # Automated tests (Pytest)
```

## Getting started

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/taskapi
cd taskapi

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn main:app --reload

# 5. Open the interactive docs
# http://localhost:8000/docs
```

## API endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Get JWT token |
| GET | `/tasks/` | Yes | Get all my tasks |
| POST | `/tasks/` | Yes | Create a task |
| GET | `/tasks/{id}` | Yes | Get one task |
| PUT | `/tasks/{id}` | Yes | Update a task |
| DELETE | `/tasks/{id}` | Yes | Delete a task |
| GET | `/tasks/summary` | Yes | Count by status |

## Running tests

```bash
pytest tests/ -v
```

## What I learned building this

- How REST APIs work — HTTP methods, status codes, request/response flow
- Why we hash passwords (bcrypt) instead of storing them plain
- How JWT tokens work — signed payload, not encrypted
- How ORMs (SQLAlchemy) map Python classes to database tables
- How to write tests that prove your API works correctly
