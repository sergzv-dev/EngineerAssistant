from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from task_broker import TaskBroker
from models import (UserInDB, UserSignUP, MessageGet, MessagesOut, Question,
                    QuestionsCreate, ServerResponse, TokenResponse)
from repository import UserRepository, MessageRepository
from security_module import hash_password, verify_password, create_access_token, verify_token
import jwt
from custom_exceptions import BrokerUnavailable
from contextlib import asynccontextmanager
from connections import init_pool, open_pg_pool_connection, close_pg_pool_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    await open_pg_pool_connection()
    yield
    await close_pg_pool_connection()

app = FastAPI(lifespan=lifespan)
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
async def signup(new_user: UserSignUP) -> ServerResponse:
    hashed_password = hash_password(new_user.password)
    data = new_user.model_dump(exclude={'password'})
    user = UserInDB(**data, hashed_password=hashed_password)
    user_id = await user_repo.add_user(user)
    return ServerResponse(obj=f'user id: {user_id}', status='created')

@app.post('/login')
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResponse:
    user = await user_repo.get_user_auth_data(form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Incorrect login or password',
                            headers={'WWW-Authenticate': 'Bearer'})
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type='bearer')


@app.post('/question')
async def question(req_data: QuestionsCreate, user_id: Annotated[int, Depends(get_current_userid)]) -> ServerResponse:
    question_data = Question(user_id=user_id, message=req_data.message)
    message_id = await message_repo.put_message(question_data)
    question_data = question_data.model_copy(update={'id': message_id})
    try:
        message_id = await t_broker.add_task(question_data)
        return ServerResponse(obj= f'message id: {message_id}', status='created')
    except BrokerUnavailable:
        raise HTTPException(status_code=503, detail='Task broker unavailable')

@app.get('/question/chat')
async def get_chat(user_id: Annotated[int, Depends(get_current_userid)],
                   limit: Annotated[int, Query(ge=1, le=100)] = 20,
                   offset: Annotated[int, Query(ge=0)] = 0,
                   ) -> MessagesOut:
    return await message_repo.get_messages(MessageGet(limit=limit, offset=offset, user_id=user_id))

#test endpoints
@app.get('/users/all')
async def all_users():
    return await user_repo.get_all_users()