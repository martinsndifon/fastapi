"""
First example api for fastapi
"""
from fastapi import FastAPI, Body

app = FastAPI()

BOOKS: list[dict[str, str]] = [
    {
        "title": "Title One",
        "author": "Author One",
        "category": "science",
    },
    {
        "title": "Title Two",
        "author": "Author Two",
        "category": "science",
    },
    {
        "title": "Title Three",
        "author": "Author Three",
        "category": "history",
    },
    {
        "title": "Title Four",
        "author": "Author Four",
        "category": "math",
    },
    {
        "title": "Title Five",
        "author": "Author Five",
        "category": "math",
    },
    {
        "title": "Title Six",
        "author": "Author Two",
        "category": "math",
    },
    {
        "title": "Title Seven",
        "author": "Author Two",
        "category": "math",
    },
]


@app.get("/books")
async def read_all_books():
    """Return all books in the Books dictionary"""
    return BOOKS


@app.get("/books/{book_title}")
async def read_book(book_title: str):
    """Return a single book from the book dictionary"""
    for book in BOOKS:
        if book.get("title").casefold() == book_title.casefold():
            return book


@app.get("/books/")
async def read_category_by_query(category: str):
    """Return books by category"""
    books_to_return = []
    for book in BOOKS:
        if book.get("category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{book_author}/")
async def read_author_catogory_by_query(book_author: str, category: str = None):
    """Return book(s) by an author and filters by category if necessary"""
    books_to_return = []
    if category:
        for book in BOOKS:
            if (
                book.get("author").casefold() == book_author.casefold()
                and book.get("category").casefold() == category.casefold()
            ):
                books_to_return.append(book)
    else:
        for book in BOOKS:
            if book.get("author").casefold() == book_author.casefold():
                books_to_return.append(book)

    return books_to_return


@app.post("/books/create_book")
async def create_book(new_book: dict[str, str] = Body()):
    """Add a new book to the BOOKS dictionary"""
    BOOKS.append(new_book)
    return new_book


@app.put("/books/update_book")
async def update_book(updated_book: dict[str, str] = Body()):
    """Update a book in the BOOKS dict"""
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == updated_book.get("title").casefold():
            BOOKS[i] = updated_book
            return updated_book


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    """Delete a book from the BOOKS dict"""
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == book_title.casefold():
            BOOKS.pop(i)
            return
