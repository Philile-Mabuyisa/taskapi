# main.py
# This is where the FastAPI app is created and everything is connected.
# Think of it as the front door of the whole project.

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, tasks

# Create all database tables on startup (if they don't exist yet)
# In production you'd use Alembic migrations instead
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskAPI",
    description="""
A personal task manager REST API built with FastAPI.

## Features
- **User accounts** — register and log in securely
- **JWT authentication** — protected routes using Bearer tokens
- **Full task CRUD** — create, read, update, delete tasks
- **Filtering** — filter tasks by status or priority
- **Summary** — get a count of tasks by status

## How to use
1. Register an account at `/auth/register`
2. Log in at `/auth/login` to get your token
3. Click **Authorize** above and paste your token
4. Use the task endpoints freely
    """,
    version="1.0.0",
)

# Register the routers — this connects all the routes to the app
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["Health"])
def root():
    """Health check — confirms the API is running"""
    return {
        "message": "TaskAPI is running!",
        "docs": "/docs",
        "version": "1.0.0"
    }
