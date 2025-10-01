# test_register_client.py

import httpx
import asyncio

LOGIN_URL = "http://127.0.0.1:8000/auth/login"
REGISTER_URL = "http://127.0.0.1:8000/auth/register"
ME_URL = "http://127.0.0.1:8000/auth/me"

async def login():
    payload = {
        "user_name": "manasji",
        "password": "n1234b",
        "email": "manas2004@gmail.com"
    }

    async with httpx.AsyncClient() as client:
        # res = await client.post(REGISTER_URL, json=payload)
        # print(res)
        response = await client.post(LOGIN_URL, json=payload)
        if response.status_code == 200:
            print("User registered successfully!")
            # print(response.json())
            return response.json()
        else:
            print(f"Failed: {response.status_code}")
            # print(response.json())

async def me(access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(ME_URL, headers=headers)
        
        if response.status_code == 200:
            print("Fetched current user successfully!")
            print(response.json())
            return response
        else:
            print(f"Failed: {response.status_code}")
            print(response.json())
            return None

if __name__ == "__main__":
    response = asyncio.run(login())
    print(response)
    print(response['access_token'])
    res = asyncio.run(me(response['access_token']))
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    # hashed = pwd_context.hash("1234")
    # print(hashed)
