from pydantic import BaseModel

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