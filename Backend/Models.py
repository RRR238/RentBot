from pydantic import BaseModel


class User_model(BaseModel):
    username: str
    password: str


class User_message_model(BaseModel):
    session_id: int
    message: str


class Chat_session_model(BaseModel):
    session_id: int

