import jwt  
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
from typing import Optional
import uuid

# Secret key should be long, random, and stored in env variables
SECRET_KEY = "YOUR_SUPER_SECRET_KEY_CHANGE_THIS"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generates a JWT access token.
    data: dictionary of claims (e.g., {"user_id": UUID, "role": str})
    """
    to_encode = data.copy()
    
    # Convert UUIDs to strings
    for k, v in to_encode.items():
        if isinstance(v, uuid.UUID):
            to_encode[k] = str(v)
    
    # Set expiration
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    """
    Verifies JWT and returns payload dict if valid.
    Returns None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        if not user_id:
            return None
        return {"user_id": user_id, "role": role}
    except (ExpiredSignatureError, InvalidTokenError):
        return None
