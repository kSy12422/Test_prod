import json
import logging
import secrets
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import redis
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)

app = FastAPI()

REDIS_CLIENT = redis.Redis(host="localhost", port=6379, db=0)

engine = create_engine('postgresql://test:2804@localhost/test')
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)

class ApiToken(Base):
    __tablename__ = 'api_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, nullable=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def generate_api_token():
    token = secrets.token_urlsafe(32)
    hashed_token = hashlib.sha3_512(token.encode()).hexdigest()
    return hashed_token

API_TOKEN = generate_api_token()
print("Сгенерированный токен API:", API_TOKEN)

class UserSchema(BaseModel):
    id: int
    username: str
    email: str

class BookSchema(BaseModel):
    id: int
    title: str
    author: str

@app.get("/api/users")
def get_users():
    all_users = session.query(User).all()
    result = [UserSchema(id=user.id, username=user.username, email=user.email) for user in all_users]
    return JSONResponse(content=result, media_type="application/json")

@app.get("/api/books")
def get_books():
    all_books = session.query(Book).all()
    result = [BookSchema(id=book.id, title=book.title, author=book.author) for book in all_books]
    return JSONResponse(content=result, media_type="application/json")

@app.post("/api/users")
def create_user(username: str, email: str):
    new_user = User(username=username, email=email)
    session.add(new_user)
    session.commit()
    return JSONResponse(content={"message": "User created successfully"}, media_type="application/json")

@app.post("/api/books")
def create_book(title: str, author: str):
    new_book = Book(title=title, author=author)
    session.add(new_book)
    session.commit()
    return JSONResponse(content={"message": "Book created successfully"}, media_type="application/json")

@app.put("/api/users/{user_id}")
def update_user(user_id: int, username: str, email: str):
    user = session.query(User).get(user_id)
    if user is None:
        return JSONResponse(content={"error": "User not found"}, status_code=404, media_type="application/json")
    user.username = username
    user.email = email
    session.commit()
    return JSONResponse(content={"message": "User updated successfully"}, media_type="application/json")

@app.put("/api/books/{book_id}")
def update_book(book_id: int, title: str, author: str):
    book = session.query(Book).get(book_id)
    if book is None:
        return JSONResponse(content={"error": "Book not found"}, status_code=404, media_type="application/json")
    book.title = title
    book.author = author
    session.commit()
    return JSONResponse(content={"message": "Book updated successfully"}, media_type="application/json")

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    user = session.query(User).get(user_id)
    if user is None:
        return JSONResponse(content={"error": "User not found"}, status_code=404, media_type="application/json")
    session.delete(user)
    session.commit()
    return JSONResponse(content={"message": "User deleted successfully"}, media_type="application/json")

@app.delete("/api/books/{book_id}")
def delete_book(book_id: int):
    book = session.query(Book).get(book_id)
    if book is None:
        return JSONResponse(content={"error": "Book not found"}, status_code=404, media_type="application/json")
    session.delete(book)
    session.commit()
    return JSONResponse(content={"message": "Book deleted successfully"}, media_type="application/json")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)