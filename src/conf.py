import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_id: str = "cv-matcher-service"
    app_name: str = "cv matcher service"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_worker_count: int = 1
    app_limit_concurrency: int = 100
    app_server_backlog: int = 100
    docs_enable: bool = True
    debug: bool = False
    log_level: str = "INFO"

    database_url: str = ""

    cache_dir: str = "cache"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    openai_model_name: str = "gpt-4o-mini"
    anthropic_model_name: str = "claude-3-5-haiku-latest"
    openai_temperature: float = 0.7
    anthropic_temperature: float = 0.7
    openai_max_tokens: int = 2000
    anthropic_max_tokens: int = 2000

    class Config:
        env_file = ".local_env" if os.path.exists(".local_env") else "env"


settings = Settings()


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s [%(request_id)s] %(name)s | %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "level": settings.log_level,
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "propagate": False,
            "level": settings.log_level,
        },
    },
}
