"use client";

import { useRouter, useSearchParams } from "next/navigation";
import {
  FormEvent,
  Suspense,
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  AlertTriangle,
  FileUp,
  Loader2,
  Trash2,
  Upload,
} from "lucide-react";

import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import {
  deleteIngestDocument,
  getClasses,
  INGEST_ACCEPT,
  ingestSizeError,
  KbDocumentRecord,
  listIngestDocuments,
  SubjectClass,
  uploadDocument,
} from "@/lib/api";

function IngestContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { tenantId } = useTenant();
  const { showToast } = useToast();

  const [classes, setClasses] = useState<SubjectClass[]>([]);
  const [classId, setClassId] = useState(searchParams.get("class_id") ?? "");
  const [title, setTitle] = useState("");
  const [lesson, setLesson] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loadingClasses, setLoadingClasses] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [documents, setDocuments] = useState<KbDocumentRecord[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadDocuments = useCallback(async () => {
    setLoadingDocuments(true);
    try {
      const result = await listIngestDocuments(tenantId, classId || undefined);
      setDocuments(result.documents);
    } catch (requestError) {
      console.error(requestError);
    } finally {
      setLoadingDocuments(false);
    }
  }, [tenantId, classId]);

  const loadClasses = useCallback(async () => {
    setLoadingClasses(true);

    try {
      const rows = await getClasses(tenantId);
      setClasses(rows);

      setClassId((current) => current || rows[0]?.id || "");
    } catch (requestError) {
      console.error(requestError);
      setError("Could not load classes for ingest.");
    } finally {
      setLoadingClasses(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadClasses();
  }, [loadClasses]);

  useEffect(() => {
    void loadDocuments();
  }, [loadDocuments]);

  useEffect(() => {
    const preselected = searchParams.get("class_id");
    if (preselected) {
      setClassId(preselected);
    }
  }, [searchParams]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!classId || !file) {
      setError("Select a class and a document.");
      return;
    }

    const sizeError = ingestSizeError(file);
    if (sizeError) {
      setError(sizeError);
      return;
    }

    setUploading(true);
    setError(null);
    setIngestStatus(null);

    try {
      const result = await uploadDocument(
        {
          classId,
          file,
          title: title.trim() || undefined,
          lesson: lesson.trim() || undefined,
        },
        tenantId,
        (document) => {
          setIngestStatus(document.status);
          void loadDocuments();
        },
      );

      const skipped = result.skipped ? " (unchanged — skipped re-ingest)" : "";

      showToast(
        `${result.source_filename ?? "document"} — ${result.chunks_upserted} chunks${skipped}.`,
        "success",
      );

      setWarnings(result.warnings ?? []);

      setFile(null);
      setTitle("");
      setLesson("");
      setIngestStatus(null);
      void loadDocuments();
      router.refresh();
    } catch (requestError) {
      console.error(requestError);
      const message =
        requestError instanceof Error
          ? requestError.message
          : "Document upload failed.";
      showToast(message, "error");
      setError(message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(documentId: string, filename: string) {
    if (!window.confirm(`Remove "${filename}" from the knowledge base?`)) {
      return;
    }
    setDeletingId(documentId);
    try {
      const result = await deleteIngestDocument(documentId, tenantId);
      showToast(`Deleted ${filename} (${result.chunks_deleted} chunks removed).`, "success");
      void loadDocuments();
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not delete document.", "error");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-heading">
          Upload Tutor Notes
        </h1>
        <p className="mt-1 text-sm text-muted">
          PDF, Word and Markdown files are chunked and added to the tenant
          knowledge base for RAG.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-4 text-fg">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="space-y-1 rounded-lg border border-blue/30 bg-blue/15 p-4 text-sm text-blue">
          <div className="flex items-center gap-2 font-medium">
            <AlertTriangle className="h-5 w-5" />
            Ingested with warnings
          </div>
          <ul className="ml-7 list-disc space-y-1">
            {warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-border bg-surface p-5"
      >
        <label className="block space-y-2">
          <span className="text-sm text-fg">Class</span>
          <select
            value={classId}
            onChange={(event) => setClassId(event.target.value)}
            disabled={loadingClasses}
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading outline-none focus:border-indigo-soft"
          >
            {classes.map((subjectClass) => (
              <option key={subjectClass.id} value={subjectClass.id}>
                {subjectClass.subject} ({subjectClass.id})
              </option>
            ))}
          </select>
        </label>

        <label className="block space-y-2">
          <span className="text-sm text-fg">Document</span>
          <input
            type="file"
            accept={INGEST_ACCEPT}
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              setWarnings([]);
              setError(null);
            }}
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-fg"
          />
        </label>

        <label className="block space-y-2">
          <span className="text-sm text-fg">Title (optional)</span>
          <input
            type="text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Lesson 7 Notes"
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading outline-none focus:border-indigo-soft"
          />
        </label>

        <label className="block space-y-2">
          <span className="text-sm text-fg">Lesson label (optional)</span>
          <input
            type="text"
            value={lesson}
            onChange={(event) => setLesson(event.target.value)}
            placeholder="7"
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading outline-none focus:border-indigo-soft"
          />
        </label>

        <button
          type="submit"
          disabled={uploading || !file || !classId}
          className="inline-flex items-center gap-2 rounded-lg bg-blue px-4 py-2 text-sm font-medium text-paper hover:bg-blue/90 disabled:opacity-50"
        >
          {uploading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Upload className="h-4 w-4" />
          )}
          {uploading && ingestStatus
            ? `Processing (${ingestStatus})…`
            : "Upload to knowledge base"}
        </button>
      </form>

      <div className="flex items-start gap-3 rounded-xl border border-border bg-surface p-4 text-sm text-muted">
        <FileUp className="mt-0.5 h-5 w-5 shrink-0" />
        <p>
          Accepts PDF with selectable text (max 50 MB), Word .docx (25 MB) and Markdown (5 MB).
          Re-uploading the same file replaces its chunks rather than duplicating them.
          Image-only scans are not supported — export as Word or Markdown first, or use a searchable PDF.
        </p>
      </div>

      <section className="space-y-3 rounded-xl border border-border bg-surface p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium text-heading">
            Ingested documents
          </h2>
          <button
            type="button"
            onClick={() => void loadDocuments()}
            className="text-sm text-muted hover:text-heading dark:text-muted hover:text-fg"
          >
            Refresh
          </button>
        </div>

        {loadingDocuments ? (
          <div className="flex items-center gap-2 text-sm text-muted">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading documents…
          </div>
        ) : documents.length === 0 ? (
          <p className="text-sm text-muted">No documents ingested yet for this class.</p>
        ) : (
          <ul className="divide-y divide-border">
            {documents.map((doc) => (
              <li
                key={doc.document_id}
                className="flex items-start justify-between gap-4 py-3 first:pt-0 last:pb-0"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium text-heading">
                    {doc.title || doc.filename}
                  </p>
                  <p className="text-xs text-muted">
                    {doc.source_type.toUpperCase()} · {doc.chunks_upserted ?? 0} chunks ·{" "}
                    {doc.status}
                    {doc.page_count ? ` · ${doc.page_count} pages` : ""}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => void handleDelete(doc.document_id, doc.filename)}
                  disabled={deletingId === doc.document_id}
                  className="inline-flex shrink-0 items-center gap-1 rounded-md border border-border px-2 py-1 text-xs text-muted hover:bg-hover disabled:opacity-50"
                >
                  {deletingId === doc.document_id ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Trash2 className="h-3 w-3" />
                  )}
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default function IngestPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-muted" />
        </div>
      }
    >
      <IngestContent />
    </Suspense>
  );
}
