# Codebase QA Tool — 規格文件

## 目標

讓 Marketing、CS、PM 等非技術人員可以用**自然語言**對 WeMo 的多個 codebase 提問，並獲得精確、可靠的回答。

**問答範例：**
- 「可以列出 Android App 中所有的 Firebase event 嗎？」
- 「可以畫出目前 iOS 的 onboarding 流程嗎？」
- 「Apollo 中機車 filter Group 0、Group 20，這邊 0 和 20 代表什麼意思？」

---

## 技術架構

### 後端
- **語言/框架**：Python 3.11+ / FastAPI
- **向量資料庫**：ChromaDB（可升級至 Qdrant）
- **LLM**：可設定切換，支援 OpenAI / Anthropic / Ollama
- **Embedding**：可設定切換（預設 `voyage-code-2`，專為程式碼訓練）
- **Code 解析**：tree-sitter（AST-based chunking，支援 TypeScript / Kotlin / Swift 等）
- **排程**：APScheduler（定時 sync）
- **Git 操作**：GitPython

### 前端
- **框架**：Next.js 14+ / TypeScript
- **UI**：Tailwind CSS + shadcn/ui
- **Diagram 渲染**：Mermaid.js

### 部署
- **容器化**：Docker Compose（FastAPI + Next.js + ChromaDB）
- **Reverse Proxy**：Nginx
- **串流**：SSE（Server-Sent Events）

---

## Codebases

| 名稱 | 類型 | 路徑 |
|------|------|------|
| mnemosyne | 資料庫 Entity 套件 | `codebases/mnemosyne` |
| mnemosyne-api | 核心營運後端 | `codebases/mnemosyne-api` |
| talos | 派工作業 API | `codebases/talos` |
| ServiceConsole-Apollo | 內部管理前台 | `codebases/ServiceConsole-Apollo` |
| UserAPP-Android | Android 用戶 App | `codebases/UserAPP-Android` |
| UserAPP-IOS | iOS 用戶 App | `codebases/UserAPP-IOS` |

---

## 核心功能

### 1. Codebase 選擇
- 預設全選（6 個 codebase 一起回答）
- 可單選或多選特定 codebase

### 2. 混合式問答策略（Hybrid Query Strategy）

系統透過 **Query Router**（輕量 LLM 分類）判斷每個問題要走哪條路：

#### Path A：RAG（快速，~2-5s）
適合問**概念、設定含義、架構說明**類問題：
- 「Group 0 / Group 20 代表什麼？」
- 「iOS 用什麼登入方式？」
- 預先建立 embedding index，retrieval 後交給 LLM 回答

#### Path B：Full Scan（完整掃描，~15-30s）
適合問**需要窮舉、列出所有項目**的問題：
- 「列出所有 Firebase event」
- 「列出所有 API endpoint」
- 將相關檔案直接送入 LLM context window 分析

#### Path C：Diagram（流程圖，~15-30s）
適合問**流程、架構圖**的問題：
- 「畫出 iOS onboarding 流程」
- 走 Full Scan 後，LLM 產生 Mermaid 語法，前端渲染

#### Path D：UI Render（頁面預覽，~15-30s）
適合問**畫面長相、UI 佈局**的問題：
- 「Apollo 的機車 filter 頁面長什麼樣子？」
- 「iOS 登入頁面的 UI 是怎麼排版的？」
- LLM 讀取相關 component code，生成 standalone HTML + Tailwind CSS
- 前端以 `<iframe sandbox="allow-scripts">` 安全渲染
- Web 頁面：全寬預覽；App 頁面：套用手機外框（iPhone 390×844 / Android 360×800）
- 介面上顯示免責說明：⚠️ 此為 AI 根據程式碼生成的**近似預覽**，非實際畫面

### 3. Code Sync
- **手動觸發**：UI 上有「Sync Now」按鈕，立即 git pull 所有 repo
- **定時排程**：可設定每天固定時間自動 pull（預設每天凌晨 3:00）
- Sync 完成後自動重新 index 有變動的 codebase

### 4. 串流回應
- 回答透過 SSE 串流顯示，使用者不用等完整回答才看到內容

### 5. 來源引用
- 每個回答都附上「參考來源」：檔案路徑 + 行號（RAG path）

### 6. LLM Provider 設定
- 透過設定檔或環境變數切換 LLM 供應商
- 不需重新部署即可切換

---

## 專案目錄結構（規劃中）

```
codebase-tool/
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── services/
│   │   │   ├── sync.py       # Git sync service
│   │   │   ├── indexer.py    # Chunking + embedding
│   │   │   ├── router.py     # Query router
│   │   │   ├── rag.py        # RAG retrieval
│   │   │   └── fullscan.py   # Full scan
│   │   ├── models/           # Pydantic models
│   │   └── config.py         # LLM / DB 設定
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Next.js
│   ├── app/
│   │   ├── page.tsx          # 主聊天介面
│   │   └── settings/         # LLM 設定頁
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── CodebaseSelector.tsx
│   │   ├── MermaidDiagram.tsx
│   │   └── SourceCitation.tsx
│   └── Dockerfile
├── codebases/                # 各 repo（git submodule 或直接 clone）
├── docker-compose.yml
├── docker-compose.prod.yml
└── SPEC.md
```

---

## Git 使用規範

### Branching Strategy
GitHub Flow：`main` 為主線，功能開發建 feature branch，完成後開 PR merge 回 main。

### Branch 命名
以 milestone 為前綴，方便追蹤：
```
feature/m1-project-setup
feature/m2-git-sync
feature/m3-rag-indexer
feature/m4-qa-rag
feature/m5-fullscan-diagram-ui-render
feature/m6-frontend-ui
feature/m7-deployment
```

### Merge 方式
Merge commit（保留完整 commit 歷史）

### 流程
```
1. 從 main 建立 feature branch
2. 開發 + commit
3. 開 PR → code review
4. Merge commit 回 main
```

---

### M1 — 基礎架構
- 建立 monorepo 結構
- FastAPI skeleton（health check、設定系統）
- Next.js skeleton（基本聊天 UI）
- Docker Compose 開發環境
- Config 系統（LLM provider、codebase 路徑）

### M2 — Git Sync 服務
- 手動觸發 git pull API
- Sync 狀態回報（成功/失敗/最後 sync 時間）
- 定時排程（APScheduler）
- 前端 Sync Now 按鈕 + 狀態顯示

### M3 — RAG 索引管線
- 程式碼智慧分割（按 function / class / file chunk）
- Embedding 產生 + 寫入 ChromaDB
- 每個 codebase 獨立 namespace
- Sync 後自動觸發增量更新（見下方 RAG 更新策略）

### M4 — 問答核心（RAG Path）
- Query Router（分類：RAG / Full Scan / Diagram）
- RAG retrieval + LLM 回答
- SSE 串流回應
- 來源引用（檔案 + 行號）

### M5 — Full Scan & Diagram & UI Render Path
- Full Scan：將相關檔案送入 LLM
- Diagram（Path C）：LLM 生成 Mermaid，前端渲染
- UI Render（Path D）：LLM 生成 HTML + Tailwind，前端以 sandboxed iframe 渲染
  - Web 預覽：全寬
  - App 預覽：套用手機外框 CSS（iOS / Android）
  - 顯示近似預覽免責說明
- 回答品質優化

### M6 — 前端完整 UI
- Codebase 多選器
- 聊天歷史
- Diagram 渲染
- LLM provider 設定頁

### M7 — 部署
- Docker Compose production 設定
- Nginx reverse proxy
- 環境變數管理
- 部署文件

---

## RAG Embedding 策略

### Chunking：AST-based 兩層結構

採用 **tree-sitter** 解析各語言 AST，以語法邊界（而非固定 token 數）切割，確保每個 chunk 都是語意完整的程式碼單元。

**支援語言對應：**

| Codebase | 語言 | tree-sitter grammar |
|----------|------|-------------------|
| mnemosyne | TypeScript | tree-sitter-typescript |
| mnemosyne-api | TypeScript | tree-sitter-typescript |
| talos | TypeScript | tree-sitter-typescript |
| ServiceConsole-Apollo | TypeScript / JavaScript | tree-sitter-typescript / tree-sitter-javascript |
| UserAPP-Android | Kotlin | tree-sitter-kotlin |
| UserAPP-IOS | Swift | tree-sitter-swift |

**兩層 Chunk 設計：**

```
Layer 1 — 細粒度 chunk（主要用於 retrieval）
  - 每個 function / method = 一個 chunk
  - 大型 class 依 method 拆分，class 定義（不含 method body）單獨一個 chunk
  - 適合「這個功能怎麼實作」「找這個 function」類問題

Layer 2 — 檔案 summary chunk（輔助用）
  - 每個檔案產生一個 summary chunk
  - 內容：前 30 行 + 所有 import + 所有 function/class 名稱列表
  - 適合「這個檔案在做什麼」「哪個檔案負責 XXX」類問題
```

**chunk metadata：**
```json
{
  "codebase": "mnemosyne-api",
  "file_path": "src/dispatchOrders/dispatchOrders.service.ts",
  "chunk_type": "function",
  "class_name": "DispatchOrdersService",
  "function_name": "createDispatchOrder",
  "start_line": 42,
  "end_line": 78,
  "language": "typescript",
  "file_hash": "sha256:abc123..."
}
```

---

### Contextual Enrichment

每個 chunk 在 embed 之前，自動加入脈絡 header，讓 embedding 帶有「這段程式碼在哪裡」的資訊，大幅提升召回率：

```
[codebase: mnemosyne-api]
[file: src/dispatchOrders/dispatchOrders.service.ts]
[class: DispatchOrdersService]
[function: createDispatchOrder]

async createDispatchOrder(dto: CreateDispatchOrderDto): Promise<DispatchOrder> {
  // ... 原始程式碼
}
```

---

### 搜尋方式：Hybrid Search（Vector + BM25）

純 vector search 對**精確識別符**（function 名稱、event 名稱、常數值）效果差，加入 BM25 keyword search 後互補：

| 問題類型 | 範例 | 主要靠 |
|---------|------|--------|
| 語意搜尋 | 「iOS onboarding 流程怎麼走」 | Vector |
| 精確識別符 | 「`logFirebaseEvent` 在哪裡用」 | BM25 |
| 混合 | 「列出所有 Firebase event 名稱」 | 兩者合併 |

最終結果以 **RRF（Reciprocal Rank Fusion）** 合併排序。

---

### Embedding Model

- **預設**：`voyage-code-2`（Voyage AI，專為程式碼訓練，對 code retrieval 效果優於通用模型）
- **可切換**：`openai/text-embedding-3-small`、`openai/text-embedding-3-large`、本地 Ollama 模型

---

## 設定檔範例（`config.yaml`）

```yaml
llm:
  provider: openai          # openai | anthropic | ollama
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}

embedding:
  provider: voyageai       # voyageai | openai | ollama
  model: voyage-code-2
  api_key: ${VOYAGE_API_KEY}

sync:
  schedule: "0 3 * * *"    # 每天凌晨 3:00（cron 格式）

codebases:
  - name: mnemosyne
    path: ./codebases/mnemosyne
    git_url: https://...
  - name: mnemosyne-api
    path: ./codebases/mnemosyne-api
    git_url: https://...
  # ...
```

---

## RAG 增量更新策略

採用**檔案 Hash 比對**（Option C），每次 sync 後只重建有變動的檔案 embedding，兼顧速度與正確性。

### 為什麼選 Hash 比對而非 Git Diff
- Git diff 在 force push / rebase 後可能不準確
- Hash 比對不依賴 git history，永遠以實際檔案內容為準
- 實作複雜度接近，但可靠性更高

### 資料模型

**ChromaDB**（每個 codebase 一個 collection）：
```
collection: "{codebase_name}"   # 例如 "mnemosyne-api"
  每個 chunk 的 metadata:
    - file_path    # 相對路徑，例如 "src/app.module.ts"
    - start_line   # chunk 起始行號
    - end_line     # chunk 結束行號
    - file_hash    # 該檔案當下的 SHA256
```

**SQLite**（本地追蹤用，`index_tracker.db`）：
```sql
CREATE TABLE indexed_files (
  codebase    TEXT,
  file_path   TEXT,
  file_hash   TEXT,
  chunk_ids   TEXT,          -- JSON array，對應 ChromaDB 的 chunk IDs
  indexed_at  TIMESTAMP,
  PRIMARY KEY (codebase, file_path)
);
```

### 更新流程

```
git pull
    ↓
掃描 codebase 所有檔案，計算每個檔案的 SHA256 hash
    ↓
與 indexed_files 表比對：

  ┌─ hash 相同 ──────────────────→ 跳過（不動）
  │
  ├─ hash 不同（檔案有修改） ──────→ 從 ChromaDB 刪除舊 chunk_ids
  │                                   → 重新 chunk + embed + 寫入 ChromaDB
  │                                   → 更新 indexed_files 記錄
  │
  ├─ 新增的檔案（不在 indexed_files）→ chunk + embed + 寫入 ChromaDB
  │                                   → 新增 indexed_files 記錄
  │
  └─ 已刪除的檔案（在 indexed_files 但不在磁碟）
                                    → 從 ChromaDB 刪除舊 chunk_ids
                                    → 從 indexed_files 刪除記錄
    ↓
更新完成，回報：新增 N 筆、更新 M 筆、刪除 K 筆
```

### 需要排除的檔案
以下類型不納入索引（避免雜訊與超出 token 限制）：

```
- node_modules/, .git/, dist/, build/, .gradle/, Pods/
- *.lock, package-lock.json, Podfile.lock
- *.png, *.jpg, *.svg, *.pdf, *.ttf, *.aar, *.framework
- *.json（設定檔可保留，大型資料檔排除）
```
