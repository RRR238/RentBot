import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

class Security_config:
    secret_key = os.getenv('SECRET_KEY')
    algorithm = os.getenv('ALGORITHM')
    issuer = os.getenv('ISSUER')
    audience = os.getenv('AUDIENCE')
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")