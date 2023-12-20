import sys

sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse

from typing import Annotated
from fastapi import Depends, APIRouter, Request, Form
from models import Base, Todos
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/todos", tags=["todos"], responses={404: {"description": "Not found"}}
)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: db_dependency):
    """Return all todos for a user"""
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
    return templates.TemplateResponse(
        "home.html", {"request": request, "todos": todos, "user": user}
    )


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    """Return the form for adding new todo"""
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "add-todo.html", {"request": request, "user": user}
    )


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    db: db_dependency,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    """Add new todo in the db"""
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, db: db_dependency, todo_id: int):
    """Return the edit todo form"""
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("id"))
        .filter(Todos.id == todo_id)
        .first()
    )
    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo, "user": user}
    )


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(
    request: Request,
    db: db_dependency,
    todo_id: int,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    """Edit a todo in the database"""
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("id"))
        .filter(Todos.id == todo_id)
        .first()
    )

    todo.title = title
    todo.description = description
    todo.priority = priority

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, db: db_dependency, todo_id: int):
    """Delete a todo from the db"""
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("id"))
        .filter(Todos.id == todo_id)
        .first()
    )

    if todo is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_404_NOT_FOUND)

    db.delete(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, db: db_dependency, todo_id: int):
    """Mark a todo as complete"""
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("id"))
        .filter(Todos.id == todo_id)
        .first()
    )

    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
