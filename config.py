from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    origins: str = ""

    class Config:
        env_file = ".env"
