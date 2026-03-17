import jwt
from datetime import datetime, timedelta
import bcrypt
from Backend.Security.Security_config import Security_config

class Security_manager:

    def __init__(self):
        self.secret_key = Security_config.secret_key
        self.algorithm = Security_config.algorithm
        self.issuer = Security_config.issuer
        self.audience = Security_config.audience

    def hash_password(self, plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_jwt_token(self, data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({
            "exp": expire,
            "iss": self.issuer,
            "aud": self.audience
        })
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return token
