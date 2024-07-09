from fastapi import Depends
from typing import Annotated
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker, Session
import urllib.parse

# Database connection details
host = "ai360-prod-ci-sqlserver.database.windows.net"
username = "ai360-admin"
password = "Alongx2024"
port = 1433
database = "ai360-prod-ci-sqldatabase"
encoded_username = urllib.parse.quote_plus(username)
encoded_password = urllib.parse.quote_plus(password)

# Ensure the driver name matches the installed driver
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{encoded_username}:{encoded_password}@{host}:1433/{database}?driver=ODBC Driver 18 for SQL Server"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"ssl_ca": "DigiCertGlobalRootCA.crt.pem"})
session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)

BASE: DeclarativeMeta = declarative_base()

def connect_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(connect_db)]
