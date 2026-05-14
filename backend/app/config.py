from __future__ import annotations

import json
from functools import lru_cache
from typing import Literal, Any

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings


class CodebaseEntry(BaseModel):
    name: str
    path: str


class Settings(BaseSettings):
    # LLM
    llm_provider: Literal["openai", "anthropic", "ollama"] = "openai"
    llm_model: str = "gpt-4o"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Embedding
    embedding_provider: Literal["voyageai", "openai", "ollama"] = "voyageai"
    embedding_model: str = "voyage-code-2"
    voyage_api_key: str = ""

    # Sync
    sync_schedule: str = "0 3 * * *"

    # ChromaDB
    chroma_persist_dir: str = "./chroma_data"

    # Codebases（JSON array string）
    codebases: list[CodebaseEntry] = []

    @field_validator("codebases", mode="before")
    @classmethod
    def parse_codebases(cls, v: Any) -> Any:
        if isinstance(v, str):
            return json.loads(v)
        return v

    @property
    def llm_api_key(self) -> str:
        if self.llm_provider == "anthropic":
            return self.anthropic_api_key
        return self.openai_api_key

    @property
    def embedding_api_key(self) -> str:
        if self.embedding_provider == "voyageai":
            return self.voyage_api_key
        return self.openai_api_key

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_config() -> Settings:
    return Settings()
