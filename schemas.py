from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str
    email: str

class BookSchema(BaseModel):
    title: str
    author: str