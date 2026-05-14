from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat():
    # TODO: M4 — Query Router + RAG / Full Scan / Diagram / UI Render
    return {"message": "Chat endpoint - coming in M4"}
