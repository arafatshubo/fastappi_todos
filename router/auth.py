from fastapi import FastAPI,APIRouter,Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import Users
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import timedelta,timezone,datetime
from router.auth import get_current_user




router=APIRouter()

bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
Outh2_bearer=OAuth2PasswordBearer(tokenUrl='token')

SECRET_KEY='3cd1459faf7c771702df88dcc4a0fe7568f28be9f645ce8dee543b19de564bd4'
ALGORITHM='HS256'

class CreateUsers(BaseModel):
  __tablename__ ='users'

 
  email :str
  username :str
  firstname :str
  lastname :str
  hash_password :str
  role :str


def authenticate_user(username,password,db):
  user=db.query(Users).filter(Users.username==username).first()
  if user is None:
    return False
  if bcrypt_context.verify(password,user.hash_password):
    return user
  return False


def create_access_token(username:str,user_id:int,role:str,expires_delta:timedelta):
  encode={'sub':username,'id':user_id,'role':role}
  expires=datetime.now(timezone.utc)+expires_delta
  encode.update({'exp':expires})
  return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

def get_current_user(token:Annotated[str,Depends(Outh2_bearer)]):
  try:
    payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    username:str =payload.get('sub')
    user_id: int =payload.get('id')
    role:str =payload.get('role')
    if username in None or user_id is None:
        raise HTTPException(status_code=404,detail='user not found')
    return {'username':username,'id':user_id,'role':role}
  except:
    raise HTTPException(status_code=404,detail='user not found')
      


def get_db():
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency=Annotated[Session,Depends(get_db)]



@router.post('/createuser/')
def create_users(new_user : CreateUsers):

  user_model=Users(
    email=new_user.email,
    userename=new_user.username,
    firstname=new_user.firstname,
    lastname=new_user.lastname,
    hash_password=bcrypt_context.hash(new_user.password),
    is_active=True,
    role=new_user.role)

  db.add(user_model)
  db.commit()
  return JSONResponse(status_code=202,content={"message":"todo created successfully"})

@router.post('/login/')
def login_user(db :db_dependency, form_data :Annotated[OAuth2PasswordRequestForm,Depends()]):
  user=authenticate_user(form_data.user_name,form_data.password,db)
  if not user:
    return "failed authication"
  token=create_access_token(user.username,user.id,user.role,timedelta(minutes=30))
  return {'access_token':token,'token_type':'bearer'}