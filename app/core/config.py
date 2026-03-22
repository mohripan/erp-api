from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Pydantic automatically reads these fields from environment variables
    or your .env file. The types are enforced — if DATABASE_URL is missing,
    it crashes at startup with a clear error. No silent misconfigs.

    This is equivalent to:
      - IOptions<AppSettings> in .NET
      - @ConfigurationProperties in Spring Boot
    """
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    APP_NAME: str = "ERP API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    DATABASE_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
settings = Settings()