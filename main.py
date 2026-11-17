from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session

from pydantic import BaseModel,Field
import models
from models import Todos
from typing import Annotated
from database import engine, SessionLocal
from fastapi.responses import JSONResponse 
from typing import Optional
from router import auth,admin
from router.auth import get_current_user


app = FastAPI()
class Todo(BaseModel):
    id :int
    title : str
    description :str = Field(max_length=100)
    priority :int=Field(gt=0,lt=100)
    completed :bool

class Todoupdate(BaseModel):
  
    title : Optional[str]
    description :Optional[str] = Field(max_length=100)
    priority :Optional[int]=Field(gt=0,lt=100)
    completed :Optional[bool]

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(admin.router)


# Pydantic model
class TodoCreate(BaseModel):
    title: str
    description: str
    priority: int
    completed: bool = False


# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]
@app.get('/')
def read_todos(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=404,detail='failed authication')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@app.get('/')
def read_specific_todos(user:user_dependency,db:db_dependency,todo_id :int):
    if user in None:
        raise HTTPException(status_code=401,detail='failed authentication')
    specific_todo=db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id ==todo_id).first()
    if specific_todo is not None:
        return specific_todo
    else:
        raise HTTPException(status_code=404,detail='to don not found')

@app.post('/create/')
def create_todos(db :db_dependency,new_todo : Todo):
    todo_model =Todos(**new_todo.model_dump())
    db.add(todo_model)
    db.commit()

    return JSONResponse(status_code=202,content={"message":"todo created successfully"})

@app.post('/create/')
def create_todos(user:user_dependency,db :db_dependency,new_todo : Todo):
    if user is None:
        raise HTTPException(status_code=401,detail='failed authication')
    todo_model =Todos(**new_todo.model_dump(),owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()

    return JSONResponse(status_code=202,content={"message":"todo created successfully"})

@app.put('/edit/{todo_id}')
def update_todos(user:user_dependency,db:db_dependency,todo_id :int,update_todo:Todoupdate):
        if user is None:
           raise HTTPException(status_code=404,detail='failed authentication')
        todo=db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id ==todo_id).first()
        if todo is None:
           raise HTTPException(status_code=404,detail='to don not found')
        
        update_data=update_todo.model_dump(exclude_unset=True)
        for key,value in update_data.items():
         setattr(todo,key,value)

        db.commit()
        return JSONResponse(status_code=202,content={"message":"todo updated successfully"})
    
@app.delete('/delete/{todo_id}')
def delete_todos(user:user_dependency,db:db_dependency,todo_id :int):
    if user is None:
        raise HTTPException(status_code=401,detail='failed authientication')
    
    todo=db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id ==todo_id).first()
    if todo is None:
           raise HTTPException(status_code=404,detail='to don not found')
    
    db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id ==todo_id).first().delete()
  

    db.commit()
    return JSONResponse(status_code=202,content={"message":"todo deleted successfully"})