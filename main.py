from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from task_broker import TaskBroker
from models import UserInDB, UserSignUP, MessageGet, MessagesOut
from repository import UserRepository, MessageRepository
from security.hash_manager import hash_password, verify_password
from security.token_manager import create_access_token, verify_token
import jwt

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = '/login')

t_broker = TaskBroker()
user_repo = UserRepository()
message_repo = MessageRepository()

def get_current_userid(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    try:
        user_id = verify_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token expired',
                            headers={'WWW-Authenticate': 'Bearer'})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token',
                            headers={'WWW-Authenticate': 'Bearer'})
    return user_id


@app.post('/signup')
async def signup(new_user: UserSignUP) -> dict:
    hashed_password = hash_password(new_user.password)
    data = new_user.model_dump(exclude={'password'})
    user = UserInDB(**data, hashed_password=hashed_password)
    user_repo.add_user(user)
    return {'message': 'User created successfully!'}

@app.post('/login')
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user = user_repo.get_user_auth_data(form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Incorrect login or password',
                            headers={'WWW-Authenticate': 'Bearer'})
    token = create_access_token(user.id)
    return {'access_token': token, 'token_type': 'bearer'}


@app.post('/question')
async def question(req_data: str, user_id: Annotated[int, Depends(get_current_userid)]) -> str:
    return t_broker.add_task(req_data)

@app.get('/question/result/{task_id}')
async def answer(task_id: str) -> str|None:
    return t_broker.get_task(task_id)

@app.get('/question/chat')
async def get_chat(limit: Annotated[int, Query(20, ge=1, le=100)],
                   offset: Annotated[int, Query(0, ge=0)],
                   user_id: Annotated[int, Depends(get_current_userid)]
                   ) -> MessagesOut:
    return message_repo.get_messages(MessageGet(limit=limit, offset=offset, user_id=user_id))

#test endpoints
@app.get('/users/all')
async def all_users():
    return user_repo.get_all_users()