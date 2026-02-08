import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timezone, timedelta

load_dotenv()

SECRET_KEY = os.getenv('AT_SECRET_KEY')
ALGORITHM = os.getenv('AT_ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('AT_EXPIRE_MINUTES'))

def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user_id),
        'iat': now,
        'exp': now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return  token

def verify_token(token: str) -> int:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload.get('sub'))