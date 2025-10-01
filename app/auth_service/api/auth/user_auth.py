from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext

from typing import Optional
from dataclasses import dataclass

from ....db_util.db_conn import get_db

from ....db_util.db_conn import get_db
from ....db_util.models import User
from ....auth_util.access_tokens import create_access_token, verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

router = APIRouter()

@dataclass
class User_Data:
    user_name: str
    password: str
    email: Optional[str]


@router.post("/register")
async def register(user_payload: User_Data, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(user_payload.user_name == User.username or user_payload.email == User.email)
    result = await db.execute(stmt)
    if(result.scalar_one_or_none()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Username or mail already exists"
        )
    # print("ans =======================> " ,user_payload.password)
    hashed_password = pwd_context.hash(user_payload.password)

    new_user = User(
        username = user_payload.user_name,
        email = user_payload.email,
        password_hash = hashed_password ,
        role = 'user',
        is_active = True,
    )

    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        print(e)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"could not add user to db ecec {e}"
            
        )
    
    return {
        "id": str(new_user.id),
        "username" : new_user.username,
        "email" : new_user.email,
        "active" : new_user.is_active,
        "role" : new_user.role,
        "cerated_at" : new_user.created_at,      
    }

@router.post("/login")
async def login(user_payload: User_Data, db: AsyncSession = Depends(get_db)):
    if(not user_payload.email and not user_payload.user_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both username and email empty"
        )

    if user_payload.email:
        stmt = select(User).where(User.email == user_payload.email)
    else:
        stmt = select(User).where(User.username == user_payload.user_name)

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not pwd_context.verify(user_payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    access_token = create_access_token({'user_id' : user.id, "role" : user.role})
    return {"access_token": access_token, "token_type": "bearer"}
    

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    print("token aa gaya oye == > ", token)
    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("user_id")
        print(f"{payload=}")
        print(f"{user_id=}")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    print("user verified")
    return user

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


