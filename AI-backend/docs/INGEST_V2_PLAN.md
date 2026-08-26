# Ingest v2 — Multi-format Document Ingestion

Upgrade the tutor-note ingest pipeline from "markdown files + flat `pypdf` text" to a
structure-preserving, multi-format pipeline covering **PDF, DOCX and Markdown**, with a
vision OCR fallback for scanned pages.

Scope agreed: PDF + DOCX + MD in Phase 1, Gemini vision OCR for image-only pages,
correctness fixes folded in as Phase 2.

---

## 1. Where we are today

| Concern | Current implementation |
|---|---|
| Markdown | `load_tenant_docs()` globs `data/knowledge_base/{slug}/*.md` |
| PDF | `run_pdf_ingest()` → `extract_pdf_text()` (`pypdf`, flat text) |
| DOCX | Not supported |
| Chunking | `RecursiveCharacterTextSplitter`, char-based, `tokens * 4` approximation |
| Storage | Qdrant only, random point IDs, no document registry |
| Execution | Synchronous inside the HTTP request via `asyncio.to_thread` |

`document_from_pdf()` and `load_tenant_docs()` both emit the same document dict
(`url`, `title`, `lesson`, `class_id`, `content`, `source_type`), which
`ingest_documents()` consumes. **That contract is good and we keep it.** Everything below
either produces that dict from more formats, or improves what happens after it.

### Known defects this plan fixes

1. **Re-ingest duplicates.** `upsert_chunks()` assigns `PointStruct(id=str(uuid.uuid4()))`
   and nothing deletes prior chunks. Re-uploading a corrected PDF leaves both versions
   competing for the same top-`k` slots. There is also no delete path at all.
2. **Parent dedup runs after `top_k`.** `search_chunks()` fetches `top_k` points, *then*
   collapses hits sharing a `parent_id`. A dense PDF page whose 4 best children share one
   parent returns **one** document instead of four. Short markdown notes rarely trigger
   this; prose-heavy PDFs trigger it constantly.
3. **`source_type` is dropped.** Set on every document dict, never copied into the Qdrant
   payload, so retrieval cannot tell a PDF citation from a markdown one.

---

## 2. Binding constraint: no torch in the runtime image

`docker/api/Dockerfile` is explicit:

> `# No Playwright / torch / local ML weights — lean runtime image.`

`compose.prod.api.yaml` runs the API on a **shared DigitalOcean droplet** alongside
another product (BookMe AI on `:8000`, Axiom on `:8001`).

This rules out the otherwise-obvious choice:

| Option | Verdict |
|---|---|
| **Docling in-process** | Rejected. Needs PyTorch + ~1–2 GB layout/table weights. |
| **`docling-serve` sidecar** | Rejected. 4.4 GB image, maintainers recommend 8–16 GB RAM, and an [unresolved memory leak](https://github.com/docling-project/docling-serve/issues/474) requires health-check restarts — unacceptable next to a co-tenant service. |
| **Hosted parse API** (LlamaParse, Mistral OCR) | Rejected as the default. Per-page cost on every document, plus a new vendor, when ~90% of tutor PDFs are born-digital and need no vision at all. |
| **Tiered local + vision fallback** | **Chosen.** See below. |

Revisit Docling if Axiom ever gets a dedicated 8 GB+ box. The extractor interface in
§3 is designed so Docling can be dropped in as one more tier without touching callers.

---

## 3. Target architecture

A format router in front of the existing `ingest_documents()`. Every tier's job is to
produce **markdown**, because that is what the chunkers already consume.

```
upload bytes
     │
     ▼
sniff_format()                 magic bytes, not the filename
     │
     ├── pdf   ──► pymupdf4llm.to_markdown(page_chunks=True)
     │                 │
     │                 └── per page: text-yield check
     │                        └── starved pages only ──► Gemini 2.5 Flash vision
     │
     ├── docx  ──► mammoth → HTML → markdownify
     │
     └── md    ──► passthrough
     │
     ▼
ExtractedDoc(markdown, pages, page_count, source_type, warnings)
     │
     ▼
document dict  ──►  ingest_documents()  ──►  chunk → embed → Qdrant
```

### Why each extractor

**PDF — `pymupdf4llm`.** Emits real markdown headings, pipe tables and per-page
metadata, in milliseconds per page, with no GPU and no model weights. It is the
strongest option that respects the lean-image constraint. `pypdf` (current) produces
flat text with no structure whatsoever.

**DOCX — `mammoth` → `markdownify`.** Mammoth maps Word's *semantic* `Heading 1`–`6`
styles onto `#`–`######` rather than guessing from font size, so a properly-styled
document survives intact. This is the same path Microsoft's MarkItDown uses internally;
we call the two libraries directly to avoid MarkItDown's large optional dependency tree
and its poor PDF converter, which we do not want.

**Legacy `.doc`** is rejected with an actionable message. Handling it needs LibreOffice
headless in the image, which is exactly the weight we are avoiding.

### OCR: per-page, not per-document

The efficiency win is routing **individual starved pages** to vision, not whole files.
A 200-page scan-cover-plus-digital-body PDF costs one page of vision, not 200.

```python
def page_needs_ocr(page_md: str, *, min_chars: int = 100, min_alpha_ratio: float = 0.5) -> bool:
    stripped = page_md.strip()
    if len(stripped) < min_chars:
        return True
    alnum = sum(c.isalnum() or c.isspace() for c in stripped)
    return (alnum / len(stripped)) < min_alpha_ratio
```

Starved pages are copied into a small in-memory PDF (`pymupdf.Document.insert_pdf`
with a page range) and sent to Gemini 2.5 Flash as inline PDF data, asking for markdown
transcription with equations as LaTeX.

Gemini is already in the stack (`langchain-google-genai`, the `merge` role). Adding an
`ocr` role in `config/param.yaml` costs nothing infrastructurally. Google does not bill
tokens for natively-embedded PDF text, and scanned pages run ~258 input tokens each —
roughly **$2 per 1,000 OCR'd pages** on 2.5 Flash, and only for pages that actually
needed it.

Hard limits to enforce before calling: 50 MB and 1,000 pages per request. Cap OCR pages
per document (`INGEST_MAX_OCR_PAGES`, default 50) so a fully-scanned 500-page textbook
fails loudly with a clear message instead of quietly running up a bill.

---

## 4. Chunking upgrade

Because every tier now emits markdown, chunking becomes structure-aware.

1. **Split on markdown headers first** (`MarkdownHeaderTextSplitter`, `#`/`##`/`###`) to
   form semantically-bounded parents; recursive-split any section over the parent budget.
2. **Prepend the heading breadcrumb to each child before embedding.** A chunk reading
   *"the value is 9.81 m/s²"* becomes *"Kinematics > Free Fall > the value is 9.81 m/s²"*.
   This is Docling's `contextualize()` pattern and it is the single highest-ROI change
   here — roughly 15 lines of code for a large retrieval gain on fragmented PDF text.
   Store the breadcrumb as `heading_path` in the payload.
3. **Count real tokens** with `tiktoken` (`cl100k_base`, matching
   `text-embedding-3-small`) instead of `PARENT_CHUNK_SIZE * 4`.
4. **Never split inside a markdown table.** Treat a table block as atomic; if it exceeds
   the child budget, emit it as its own chunk and repeat the header row.

---

## 5. Phase 1 — extraction router

### New module: `src/services/ingest_service/extractors/`

```
extractors/
├── __init__.py       extract_document() — the router
├── base.py           ExtractedDoc, PageText dataclasses; ExtractionError
├── sniff.py          sniff_format() from magic bytes
├── pdf.py            pymupdf4llm + OCR routing
├── docx.py           mammoth + markdownify
├── markdown.py       passthrough + front-matter strip
└── ocr.py            Gemini vision transcription
```

```python
@dataclass(frozen=True)
class PageText:
    page_number: int          # 1-based
    markdown: str
    ocr_used: bool = False


@dataclass(frozen=True)
class ExtractedDoc:
    markdown: str
    source_type: str                  # "pdf" | "docx" | "markdown"
    pages: list[PageText] | None      # None for formats without pagination
    page_count: int | None
    ocr_page_count: int = 0
    warnings: list[str] = field(default_factory=list)
```

`sniff_format()` reads magic bytes rather than trusting the extension: `%PDF-` for PDF;
`PK\x03\x04` plus a `word/document.xml` entry in the zip for DOCX; `\xd0\xcf\x11\xe0`
(OLE2) means legacy `.doc` → reject with *"Save as .docx and re-upload"*.

### Changed files

| File | Change |
|---|---|
| `ingest_service/pdf_loader.py` | Delete; superseded by `extractors/pdf.py` |
| `ingest_service/pipeline.py` | `run_pdf_ingest` → `run_upload_ingest`, format-agnostic; keep a thin `run_pdf_ingest` alias for one release |
| `api/routers/tools/ingest.py` | Accept PDF/DOCX/MD; validate via sniff, not extension; per-format size caps |
| `api/schemas.py` | `IngestUploadResponse` gains `source_type`, `page_count`, `ocr_pages`, `warnings` |
| `infrastructure/db/qdrant_client.py` | Propagate `source_type`, `page_number`, `heading_path` into payloads |
| `ingest_service/chunkers.py` | Header-aware split, breadcrumb contextualization, `tiktoken` counting |
| `config/param.yaml` | `ingest:` block (see §7) + `llm.roles.ocr` |
| `requirements.txt` | Add `pymupdf4llm`, `mammoth`, `markdownify`, `tiktoken` |
| Dashboard `ingest/page.tsx` | `accept` → `.pdf,.docx,.md`; client-side size guard |
| Dashboard `classes/page.tsx` | Same `accept`; add the missing success toast |
| Dashboard `lib/api.ts` | Make `uploadClassDocument` use `aiRequest` — it currently sends **no auth headers**, unlike `uploadDocument` |

### Licensing note

`pymupdf4llm` is AGPL-3.0. This repo is GPL-3.0, so they are compatible (GPLv3 §13
permits it). Flagging it because a future commercial relicense would require a
commercial licence from Artifex.

---

## 6. Phase 2 — correctness and lifecycle

### Idempotent re-ingest

```python
document_id = hashlib.sha256(content).hexdigest()[:16]
point_id    = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{document_id}:{chunk_index}"))
```

Before upserting, delete by filter on `document_id` (needs a keyword payload index
alongside the existing `class_id` one). Re-uploading a corrected file then *replaces*
rather than duplicates. If the hash is unchanged, short-circuit the whole pipeline —
no extraction, no embedding spend.

### Over-fetch before parent dedup

In `search_chunks()`, query `top_k * 3` points, collapse same-parent hits, then trim to
`top_k`. Fixes the silent result-count collapse on dense documents.

### Document registry — `kb_documents`

Net-new; document metadata currently lives only in Qdrant payloads, so there is no way
to list or delete a document.

```sql
CREATE TABLE IF NOT EXISTS kb_documents (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    class_id        TEXT NOT NULL REFERENCES subject_classes(id) ON DELETE CASCADE,
    document_id     TEXT NOT NULL,           -- sha256(bytes)[:16]
    filename        TEXT NOT NULL,
    title           TEXT,
    lesson          TEXT,
    source_type     TEXT NOT NULL,           -- pdf | docx | markdown
    byte_size       BIGINT NOT NULL,
    page_count      INT,
    ocr_pages       INT NOT NULL DEFAULT 0,
    chunks_upserted INT,
    status          TEXT NOT NULL DEFAULT 'pending',
    error           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, document_id)
);
```

`status ∈ {pending, extracting, embedding, ready, failed}` — the same column serves the
Phase 3 async job model, so it costs nothing to add now.

### New endpoints

- `GET /tools/ingest/documents?tenant_id=&class_id=` — list the registry
- `DELETE /tools/ingest/documents/{document_id}` — delete Qdrant points by filter, then the row

---

## 7. Configuration

```yaml
ingest:
  max_upload_mb:
    pdf: 50
    docx: 25
    markdown: 5
  ocr:
    enabled: true
    min_chars_per_page: 100
    min_alpha_ratio: 0.5
    max_pages_per_doc: 50
  chunking:
    respect_markdown_headers: true
    contextualize_children: true
    token_encoding: cl100k_base

llm:
  roles:
    ocr:
      provider: google
      tier: general
```

---

## 8. Test plan

Existing tests that **must** be updated:

- `tests/test_ingest_upload.py::test_ingest_upload_rejects_non_pdf` — asserts `.txt` → 422.
  Becomes "rejects unsupported types", with `.docx` and `.md` now accepted.
- `tests/test_ingest_pipeline.py::test_run_pdf_ingest` — mocks `extract_pdf_text`, which
  Phase 1 deletes. Re-point at `extract_document`.

New coverage:

- `sniff_format()` — correct format for each magic-byte prefix; a `.pdf`-named DOCX is
  detected as DOCX; OLE2 `.doc` raises a clear `ExtractionError`.
- DOCX extraction — `Heading 1` → `#`, nested lists, a table round-trips to pipes.
- `page_needs_ocr()` — boundary cases at `min_chars` and `min_alpha_ratio`.
- OCR router — with Gemini mocked, only starved page indices are sent.
- Contextualization — child text carries its heading breadcrumb.
- Idempotency (Phase 2) — ingesting identical bytes twice leaves the point count flat.
- Over-fetch (Phase 2) — 4 same-parent children still return 4 distinct documents.

Fixture files needed under `tests/fixtures/`: a small born-digital PDF, a scanned PDF,
a styled DOCX, and a DOCX containing a merged-cell table.

---

## 9. Risks

| Risk | Mitigation |
|---|---|
| `pymupdf4llm` kwargs shift between releases (`use_ocr`, `table_output` / `table_strategy`) | Pin an exact version; verify the installed signature before wiring options |
| Merged-cell DOCX tables flatten through `markdownify` | Accept for v1; emit a warning on the document. HTML table passthrough is the escape hatch |
| Gemini OCR latency on a large scan pushes past the HTTP timeout | `max_pages_per_doc` cap in Phase 1; async jobs in Phase 3 |
| Equations in tutor notes come out garbled | Prompt Gemini for LaTeX; add a physics/chemistry PDF to the eval set |

---

## 9a. Findings from Phase 1 implementation

Three things differed from the assumptions above and are worth recording.

**Image footprint is ~190 MB, not ~30 MB.** Current `pymupdf4llm` (1.28.x, versioned
in lockstep with `pymupdf`) runs a GNN layout model and pulls `onnxruntime` (80 MB)
alongside `pymupdf` (110 MB). The mitigating detail is that the ONNX weights ship
*inside the wheels* (`pymupdf/layout/resources/onnx/`), so there is no startup
download and no network dependency at inference — the container stays
self-contained. Still an order of magnitude below torch plus the Docling model set.
`pymupdf4llm` is imported lazily inside the PDF extractor so the API process does
not pay the ~1s onnxruntime import unless a PDF is actually ingested.

**pymupdf4llm's `ocr_function` hook is the wrong shape for a vision model.** It calls
back with `(page, dpi=, language=, keep_ocr_text=)` and expects the callee to insert
positioned text spans into the page. A VLM returns prose without bounding boxes. The
implementation therefore extracts starved pages into a single-page in-memory PDF and
splices the returned markdown back at the page position, which also keeps the output
in markdown rather than untyped spans.

**mammoth alone is not enough for real-world DOCX.** The repo's own
`docs/*.docx` files contain **no `w:pStyle` elements at all** — headings were made by
direct character formatting, not Word's Heading styles. mammoth is right to refuse to
promote those, but the result is a completely flat document, which defeats
breadcrumb contextualization. `extractors/docx.py` therefore recovers headings from
standalone bold paragraphs (short, no terminal punctuation, blank-line delimited),
inferring depth from any `1.` / `1.2` section numbering, and always attaches a warning
so the tutor can see it happened. On the repo's own MVP document this recovers 11
headings and produces a *cleaner* tree than the PDF of the same file.

A fourth, smaller one: the heading breadcrumb is capped at 80 characters, dropping
the shallowest levels first. A document whose H1 is a long title would otherwise
spend ~12% of every child chunk's token budget on a prefix identical across the
whole document.

---

## 10. Deferred to Phase 3+

- Async ingest — `BackgroundTasks` (pattern already proven in `api/webhooks/twilio.py`)
  driving `kb_documents.status`, with the Dashboard polling. No queue infrastructure needed.
- Stop duplicating `parent_text` across all 5–6 of a parent's children (~6x payload
  bloat); store parents once and join on retrieval.
- Google Docs via Drive `files.export` as `text/markdown` — the service account already
  exists in `drive_service/`, and it needs no parsing at all.
- PPTX / XLSX.
- A golden-set retrieval eval harness, so parser changes can be measured rather than
  assumed.
