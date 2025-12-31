from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    WHAPI_BASE_URL: str
    WHAPI_TOKEN: str

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"   
    )

settings = Settings()
