from fastapi import Body, FastAPI
from pydantic import BaseModel
from typing import Union

app = FastAPI()


class Book:
    """Class for the book object"""

    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id, title, author, description, rating):
        """Initialize a new book"""
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


class BookRequest(BaseModel):
    """Provides data validation using pydantic BaseModel"""

    id: int
    title: str
    author: str
    description: str
    rating: int


BOOKS = [
    Book(1, "Computer Science Pro", "Martins", "A very nice book", 5),
    Book(2, "Be Fase with FastAPI", "Martins", "A great book", 5),
    Book(3, "Computer Science Pro", "Martins", "A very nice book", 5),
    Book(4, "HP1", "Author 1", "Book Description", 2),
    Book(5, "HP2", "Author 2", "Book Description", 3),
    Book(6, "HP3", "Author 3", "Book Description", 1),
]


@app.get("/books")
async def read_all_books():
    """Return all the books from the API"""
    return BOOKS


@app.post("/create-book")
async def create_book(book_request: BookRequest):
    """Create a new book in the api"""
    BOOKS.append(book_request)
    return book_request
