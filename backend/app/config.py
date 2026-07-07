import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Saarthi Wealth Avatar API"
    database_url: str = "sqlite:///./saarthi.db"

    # Optional: if unset, the avatar falls back to a rule-based templated responder
    # so the whole app still runs end-to-end with zero paid API keys during a demo.
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    demo_customer_id: str = "SAARTHI100000"
    seed_customer_count: int = 200

    demo_staff_id: str = "STAFF001"
    demo_staff_password: str = "saarthi-demo"


settings = Settings()
