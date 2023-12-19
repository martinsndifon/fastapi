"""
Database module
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Database connection for sqlite3 db
"""
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
"""

# Database connection for postgres db
""" SQLALCHEMY_DATABASE_URL = os.environ.get("POSTGRES_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL) """

# Database connection for mysql db
SQLALCHEMY_DATABASE_URL = os.environ.get("MYSQL_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
