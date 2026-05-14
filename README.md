# WeMo Codebase QA Tool

讓 Marketing、CS、PM 用自然語言問 WeMo codebase 問題。

## 需求

- Python 3.11+
- Node.js 20+
- npm 10+

---

## 本機啟動

### 1. 後端（FastAPI）

```bash
cd backend

# 建立虛擬環境（第一次）
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 安裝依賴（第一次）
pip install -r requirements.txt

# 複製設定檔並填入 API key
cp .env.example .env
# 編輯 .env，填入 OPENAI_API_KEY、VOYAGE_API_KEY 等

# 啟動
uvicorn app.main:app --reload
```

後端跑在 → http://localhost:8000

### 2. 前端（Next.js）

```bash
cd frontend

# 安裝依賴（第一次）
npm install

# 啟動
npm run dev
```

前端跑在 → http://localhost:3000

---

## 設定（`backend/.env`）

從 `.env.example` 複製後修改，所有設定統一在這一個檔案：

```env
# LLM
LLM_PROVIDER=openai        # openai | anthropic | ollama
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...

# Embedding
EMBEDDING_PROVIDER=voyageai
EMBEDDING_MODEL=voyage-code-2
VOYAGE_API_KEY=pa-...

# Codebases（JSON array）
CODEBASES=[{"name":"mnemosyne","path":"./codebases/mnemosyne"},...]
```

> `.env` 已在 `.gitignore` 排除，不會被 commit。

---

## 專案結構

```
codebase-tool/
├── backend/          # FastAPI
│   ├── app/
│   │   ├── api/      # health, chat, sync endpoints
│   │   ├── services/ # sync, indexer, router, rag, fullscan（M2–M5）
│   │   ├── models/   # Pydantic models
│   │   ├── config.py # 設定系統
│   │   └── main.py
│   ├── config.example.yaml
│   └── requirements.txt
├── frontend/         # Next.js 14
│   ├── app/          # page.tsx, layout.tsx
│   ├── components/   # ChatInput, MessageBubble, CodebaseSelector
│   └── lib/api.ts    # API client
├── codebases/        # 各 repo（.gitignore 排除，由 sync 服務管理）
└── SPEC.md
```

---

## API Endpoints

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/health` | 健康檢查 |
| POST | `/api/chat` | 問答（SSE 串流）|
| POST | `/api/sync` | 手動觸發 git pull |
| GET | `/api/sync/status` | 查詢 sync 狀態 |

---

## Milestones

- [x] **M1** 基礎架構（FastAPI + Next.js + Config）
- [ ] **M2** Git Sync 服務
- [ ] **M3** RAG 索引管線
- [ ] **M4** 問答核心（RAG Path + SSE）
- [ ] **M5** Full Scan + Diagram + UI Render
- [ ] **M6** 前端完整 UI
- [ ] **M7** 部署（Docker + Nginx）
