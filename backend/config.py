from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    t212_api_key: str
    t212_base_url: str = "https://live.trading212.com"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "maybank"
    postgres_user: str = "maybank"
    postgres_password: str

    redis_host: str = "localhost"
    redis_port: int = 6379

    duckdb_path: str = "./data/maybank.duckdb"

    class Config:
        env_file = ".env"


settings = Settings()
