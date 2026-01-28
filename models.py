from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    username: str
    email: str|None = None

class UserInDB(User):
    hashed_password: str

#sign up
class UserSignUP(BaseModel):
    username: str
    password: str
    email: str

#log in
class UserLoginInDB(BaseModel):
    id: int
    hashed_password: str

#messages
class MessageModel(BaseModel):
    id: int | None = None
    user_id: int
    message: str
    message_type: str
    created_at: datetime | None = None

class Question(MessageModel):
    message_type: str = "Q"

class Answer(MessageModel):
    message_type: str = "A"

class MessageGet(BaseModel):
    user_id: int
    limit: int
    offset: int

class MessagesOut(BaseModel):
    limit: int
    offset: int
    total: int
    data: list[MessageModel]