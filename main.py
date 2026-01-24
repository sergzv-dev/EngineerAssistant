from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from task_broker import TaskBroker
from models import User,UserInDB, UserSignUP
from repository import UserRepository
from security import hash_password

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')

t_broker = TaskBroker()
user_repo = UserRepository()

def get_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    pass

@app.post('/signup')
async def signup(new_user: UserSignUP) -> dict:
    hashed_password = hash_password(new_user.password)
    data = new_user.model_dump(exclude={'password'})
    user = UserInDB(**data, hashed_password=hashed_password)
    user_repo.add_user(user)
    return {'message': 'User created successfully!'}


@app.post('/question')
async def question(req_data: Annotated[str, Depends(get_user)]) -> str:
    return t_broker.add_task(req_data)

@app.get('/question/result/{task_id}')
async def answer(task_id: str) -> str|None:
    return t_broker.get_task(task_id)

#test endpoints
@app.get('/users/all')
async def all_users():
    return user_repo.get_all_users()