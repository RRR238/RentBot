from sqlalchemy.ext.asyncio import AsyncSession
from Database.Session_config import AsyncSessionLocal
from Backend.Security.Security_config import Security_config
from langchain.chat_models import ChatOpenAI
import jwt
from fastapi import Depends, HTTPException


def get_chat_model() -> ChatOpenAI:
    return ChatOpenAI(temperature=0.2, model_name="gpt-4o")


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


def endpoint_verification(token: str = Depends(Security_config.oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            Security_config.secret_key,
            algorithms=[Security_config.algorithm],
            audience=Security_config.audience,
            issuer=Security_config.issuer
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except (jwt.InvalidTokenError, jwt.DecodeError, jwt.PyJWTError):
        raise HTTPException(status_code=401, detail="Invalid or malformed token")