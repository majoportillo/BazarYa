import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

USER_DB = os.getenv("USER_DB", "miuser")
PASSWORD_DB = os.getenv("PASSWORD_DB", "mipass")
HOST_DB = os.getenv("HOST_DB", "localhost")
PORT_DB = os.getenv("PORT_DB", "54322")
NAME_DB = os.getenv("NAME_DB", "bazar")

DATABASE_URL = f"postgresql+psycopg2://{USER_DB}:{PASSWORD_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()