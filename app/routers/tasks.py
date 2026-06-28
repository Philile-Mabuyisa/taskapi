# app/routers/tasks.py
# All task endpoints. Every route requires a logged-in user.
#
# GET    /tasks          — get all MY tasks (with optional filters)
# POST   /tasks          — create a new task
# GET    /tasks/{id}     — get one task
# PUT    /tasks/{id}     — update a task
# DELETE /tasks/{id}     — delete a task
# GET    /tasks/summary  — count by status

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Task, TaskStatus, TaskPriority, User
from app.schemas.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 must be logged in
):
    """
    Returns a count of tasks by status.
    Great for a dashboard — shows how many are todo / in progress / done.
    """
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    return {
        "total": len(tasks),
        "todo": sum(1 for t in tasks if t.status == TaskStatus.todo),
        "in_progress": sum(1 for t in tasks if t.status == TaskStatus.in_progress),
        "done": sum(1 for t in tasks if t.status == TaskStatus.done),
        "high_priority": sum(1 for t in tasks if t.priority == TaskPriority.high),
    }


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 must be logged in
):
    """
    Get all tasks for the logged-in user.
    Optional query params: ?status=todo or ?priority=high
    Example: GET /tasks?status=todo&priority=high
    """
    # Start with a query for this user's tasks only
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    # Apply optional filters
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    return query.order_by(Task.id.desc()).all()


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 must be logged in
):
    """Create a new task for the logged-in user."""
    new_task = Task(
        **task_data.model_dump(),  # unpack all fields from the schema
        owner_id=current_user.id   # link to the logged-in user
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 must be logged in
):
    """Get a single task by ID — only if it belongs to the logged-in user."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id  # security: can't see other users' tasks
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 must be logged in
):
    """
    Update a task. Only send the fields you want to change.
    Example: {"status": "done"} — just updates status, leaves everything else.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only update fields that were actually sent (exclude_unset=True)
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 must be logged in
):
    """Delete a task. Returns 204 No Content on success."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    # 204 means success with no response body
