from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Ollama settings
    ollama_host: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.1"

    # Application settings
    data_dir: str = "/data"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
