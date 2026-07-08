from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Todo API", version="1.0.0")

class Todo(BaseModel):
    id: int
    title: str
    done: bool = False

todos: list[Todo] = []

@app.get("/todos")
def list_todos() -> list[Todo]:
    return todos

@app.post("/todos")
def create_todo(todo: Todo) -> Todo:
    todos.append(todo)
    return todo
