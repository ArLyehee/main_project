from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db" #'oracle+cx_oracle://admin:1234@localhost:1521/?service_name=xe'

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite 용
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
