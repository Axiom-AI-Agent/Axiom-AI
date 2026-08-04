# Google Drive MCP — Integration & Testing

How to connect a tuition institute's Google Drive to Axiom AI, and how to test the `axiom-drive` MCP server locally.

**Drive** = send file links (past papers, textbooks, syllabus).  
**RAG (Qdrant)** = answer questions from tutor notes — see [ingest script](../scripts/ingest_tenant_notes.py), not Drive.

---

## Architecture

```text
Student (WhatsApp / POST /chat)
        │
        ▼
Resource agent  ──►  drive vs rag sub-router
        │
        ▼ (drive path)
axiom-drive MCP  (src/mcp_servers/drive_server.py)
        │
        ▼
DriveTool  (src/agents/tools/drive_tool.py)
        │
        ├── Supabase  tenants.drive_folder_id  (per institute)
        └── Google Drive API  (service account, read-only)
                └── {root}/papers/ | textbooks/ | syllabus/
```

| Component | Path |
|-----------|------|
| MCP server | `src/mcp_servers/drive_server.py` |
| MCP config | `src/mcp_servers/mcp_config.py` → `axiom-drive` |
| Business logic | `src/agents/tools/drive_tool.py` |
| Google client | `src/services/drive_service/drive_client.py` |
| Debug REST | `POST /tools/drive/search`, `POST /tools/drive/list` |

**MCP tools:** `drive_search`, `drive_list`  
**Allowed folders only:** `papers`, `textbooks`, `syllabus` (enforced in `DriveTool`).

Agents call Drive **via MCP** when `AGENT_USE_MCP=true`; otherwise they use the same `DriveTool` in-process (`src/agents/runtime.py` fallback).

---

## Platform setup (once)

### 1. Google Cloud

1. [Google Cloud Console](https://console.cloud.google.com/) → create/select project  
2. Enable **Google Drive API**  
3. Create a **Service account** → download JSON key  
4. Copy the service account email (e.g. `axiom-drive@project.iam.gserviceaccount.com`)

### 2. Environment

In `.env`:

```bash
DRIVE_MOCK=false
GOOGLE_SERVICE_ACCOUNT_JSON=/absolute/path/to/service-account.json
AGENT_USE_MCP=true          # optional; use MCP subprocess path (Python 3.10+)
```

For local dev without Google credentials:

```bash
DRIVE_MOCK=true
```

Default mock backend is **empty** — searches return `"files": []` but prove wiring. Use [smoke script](#step-1--smoke-test-no-server) or real Drive for files.

---

## Per-institute onboarding

### Folder layout

Ask the institute to create:

```text
{Institute Root}/          ← one root folder per tenant
├── papers/                ← past papers, model papers, tutes
├── textbooks/             ← textbook PDFs
└── syllabus/              ← syllabus, intro packs
```

Do **not** rely on Drive for tutor lesson Q&A — ingest notes to Qdrant instead.

### Share with service account

1. Open the institute's **root folder** in Google Drive  
2. **Share** → add the service account email  
3. Role: **Viewer** (read-only)

### Folder ID

From the URL:

```text
https://drive.google.com/drive/folders/1ABCxyzROOT_ID_HERE
```

### Supabase tenant row

Set `drive_folder_id` on the tenant (see [DATABASE.md](DATABASE.md) → `tenants`):

```sql
INSERT INTO tenants (id, name, slug, status, whatsapp_number, drive_folder_id)
VALUES (
  'tenant-acme-physics',
  'Acme Physics Institute',
  'acme-physics',
  'active',
  'whatsapp:+94XXXXXXXXX',
  '1ABCxyzROOT_ID_HERE'
);

-- Or update existing:
UPDATE tenants
SET drive_folder_id = '1ABCxyzROOT_ID_HERE', updated_at = NOW()
WHERE id = 'tenant-demo-physics';
```

Demo seed uses placeholder IDs (`drive-folder-physics-demo`) — replace with **real** Google folder IDs for production.

### Tutor notes (RAG, separate step)

```bash
# Markdown under data/knowledge_base/{tenant-slug}/
PYTHONPATH=src python scripts/ingest_tenant_notes.py --tenant-id tenant-acme-physics
```

---

## Onboarding checklist

| # | Task | Owner |
|---|------|--------|
| 1 | Service account + Drive API enabled | Platform |
| 2 | `GOOGLE_SERVICE_ACCOUNT_JSON` + `DRIVE_MOCK=false` in `.env` | Platform |
| 3 | Institute creates `papers/`, `textbooks/`, `syllabus/` | Institute |
| 4 | Share root folder with service account (Viewer) | Institute |
| 5 | Set `tenants.drive_folder_id` in Supabase | Platform |
| 6 | Upload PDFs to subfolders | Institute |
| 7 | Ingest tutor notes to Qdrant (optional) | Platform |
| 8 | Test `/tools/drive/search` and `/chat` | Platform |

---

## Testing

### Prerequisites

```bash
cd /path/to/Axiom-AI
source .venv/bin/activate   # Python 3.11 for MCP
make run                    # for REST / chat tests
```

### Step 1 — Smoke test (no server)

Injects mock Drive files; proves tool + resource agent:

```bash
PYTHONPATH=src python scripts/smoke_resource.py
```

Expect: `[OK] Drive search: 2024-model-paper-physics.pdf`

### Step 2 — MCP subprocess (`axiom-drive` only)

```bash
PYTHONPATH=src python - <<'PY'
import asyncio, os, sys
sys.path.insert(0, "src")
from dotenv import load_dotenv
load_dotenv(".env", override=True)
os.environ["LANGFUSE_ENABLED"] = "false"

async def main():
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from mcp_servers.mcp_config import build_mcp_server_config

    cfg = build_mcp_server_config()
    client = MultiServerMCPClient({"axiom-drive": cfg["axiom-drive"]})
    tools = await client.get_tools()
    print("MCP tools:", [t.name for t in tools])

    search = next(t for t in tools if t.name == "drive_search")
    raw = await search.ainvoke({
        "tenant_id": "tenant-demo-physics",
        "query": "physics paper",
        "folder": "papers",
    })
    print("drive_search:", raw)

asyncio.run(main())
PY
```

Success: tools `drive_search`, `drive_list` listed; JSON with `"ok": true`.

### Step 3 — REST debug (same logic as MCP)

```bash
curl -s -X POST http://localhost:8000/tools/drive/search \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-demo-physics",
    "query": "physics paper",
    "folder": "papers"
  }' | python3 -m json.tool

curl -s -X POST http://localhost:8000/tools/drive/list \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-demo-physics",
    "folder": "papers"
  }' | python3 -m json.tool
```

Swagger: http://localhost:8000/docs → **Tools — Drive**

### Step 4 — Full chat (agent + MCP)

`.env`:

```bash
AGENT_USE_MCP=true
DRIVE_MOCK=false   # when using real Drive
```

Restart server, then send a **Drive-routed** message (papers / textbook / syllabus — not “explain from notes”):

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-demo-physics",
    "phone": "94771234567",
    "message": "Do you have past papers for 2024 physics?"
  }' | python3 -m json.tool
```

Server logs should include `axiom-drive` when MCP is active.

### Router disambiguation (Drive vs RAG)

| Student message | Path | Tool |
|-----------------|------|------|
| "Can I get last week's physics paper?" | Drive | `drive_search` |
| "Send me the textbook for chapter 3" | Drive | `drive_search` |
| "Explain velocity from lesson 5" | RAG | `kb_search` |
| "What did sir say about Newton's laws?" | RAG | `kb_search` |

---

## Multi-tenant isolation

- Each tenant has its own `drive_folder_id` → separate Drive tree  
- Tool calls always include `tenant_id`; Tenant A cannot access Tenant B files  
- Qdrant collections are also tenant-scoped: `axiom_kb_{tenant_id}`

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `"files": []` | Mock empty, SA not shared, wrong folder ID, files in wrong subfolder | Share folder; verify ID; check `papers/` layout |
| `Unknown tenant or missing drive_folder_id` | No row or null `drive_folder_id` | Run seed / `UPDATE tenants SET drive_folder_id=...` |
| Still mock behaviour | `DRIVE_MOCK=true` | Set `DRIVE_MOCK=false`, restart |
| Chat uses RAG not Drive | Message sounds like explanation | Use "past paper", "textbook", "syllabus" |
| MCP import error | Python 3.9 or missing packages | Python 3.11 venv, `pip install -r requirements.txt` |
| Permission / 403 from Google | Folder not shared with SA | Share root as Viewer |
| Links don't open for students | Drive link sharing policy | Institute adjusts file/folder sharing |

---

## MVP vs v2

| | MVP (current) | v2 (planned) |
|---|---------------|--------------|
| Auth | One platform service account | OAuth per institute |
| Credentials | `GOOGLE_SERVICE_ACCOUNT_JSON` in `.env` | Per-tenant token in `tenant_integrations` |
| Folder map | `tenants.drive_folder_id` | Same + optional per-tenant OAuth |

See [AI Backend Roadmap](Technical%20Docs/AI%20backend%20-%20Roadmap.md) §6 (Resource Split) and Phase 4.

---

## Phase 4 closure

```bash
make ingest-demo          # Qdrant: physics + chemistry demo notes
make smoke-phase4         # mock Drive link + mock RAG citation
make smoke-phase4-live    # + live Qdrant RAG (after ingest)
```

Production strict mode: `AGENT_USE_MCP=true` and `ALLOW_INPROCESS_TOOLS=false`.

See [DRIVE_INTEGRATION.md](DRIVE_INTEGRATION.md) for real Google Drive (test separately).

---

## Related docs

- [DEV_CHAT.md](DEV_CHAT.md) — local chat testing  
- [DATABASE.md](DATABASE.md) — `tenants.drive_folder_id`  
- [AI Backend Roadmap](Technical%20Docs/AI%20backend%20-%20Roadmap.md) — Phase 4 Resource Agent
