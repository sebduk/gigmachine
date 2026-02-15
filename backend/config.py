from __future__ import annotations

import json
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "mysql+aiomysql://gigfinder:gigfinder@localhost:3306/gigfinder"

    # Application
    app_env: str = "development"
    secret_key: str = "change-me-in-production"
    cors_origins: str = '["http://localhost:5173"]'

    # Scraping
    scrape_user_agent: str = "GigFinder/0.1 (academic job board)"

    # Privacy
    data_retention_days: int = 0  # 0 = keep forever
    pii_strip_enabled: bool = True

    @property
    def cors_origin_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


settings = Settings()
