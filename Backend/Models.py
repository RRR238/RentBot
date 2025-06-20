from pydantic import BaseModel

class User_model(BaseModel):
    username: str
    password: str
