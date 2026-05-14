from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import get_config

app = FastAPI(
    title="Codebase QA Tool",
    description="自然語言問答 WeMo codebases",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def startup():
    cfg = get_config()
    print(f"✅ LLM: {cfg.llm_provider}/{cfg.llm_model}")
    print(f"✅ Embedding: {cfg.embedding_provider}/{cfg.embedding_model}")
    print(f"✅ Codebases: {[c.name for c in cfg.codebases]}")
