import os

import dotenv
from fastapi import HTTPException, Header


def check_auth(authorization: str = Header(None)):

    dotenv.load_dotenv()

    SECRET_KEY = os.getenv("SECRET_KEY")

    """Проверка API-токена"""
    if authorization != f"Bearer {SECRET_KEY}":
        raise HTTPException(status_code=403, detail="Access denied")
    return True