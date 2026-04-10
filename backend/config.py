import os
from dotenv import load_dotenv

load_dotenv()

T212_API_KEY = os.environ["T212_API_KEY"]
T212_BASE_URL = os.environ.get("T212_BASE_URL", "https://live.trading212.com")

POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT"))
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "./data/maybank.duckdb")
