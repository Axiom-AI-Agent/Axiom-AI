"""TEMP DEBUG — full Google Drive MCP integration protocol (Steps 1–12).

Does not mutate production data. Run:
  PYTHONPATH=src .venv/bin/python scripts/debug_drive_integration.py
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=True)
sys.path.insert(0, str(ROOT / "src"))

TENANT_ID = os.getenv("DEBUG_DRIVE_TENANT_ID", "tenant-demo-physics")
SEARCH_QUERY = os.getenv("DEBUG_DRIVE_QUERY", "physics paper")
CLASS_IDS = [
    cid.strip()
    for cid in os.getenv("DEBUG_DRIVE_CLASS_IDS", "class-physics-al-2026").split(",")
    if cid.strip()
]
PLACEHOLDER_FOLDER_IDS = {
    "drive-folder-physics-demo",
    "drive-folder-chemistry-demo",
}


def _mask_path(path: str) -> str:
    if not path:
        return "(empty)"
    p = Path(path)
    return f".../{p.name} (abs_len={len(path)})"


def step1_environment() -> dict:
    print("\n=== STEP 1 — Environment ===")
    drive_mock = os.getenv("DRIVE_MOCK", "")
    sa_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    agent_use_mcp = os.getenv("AGENT_USE_MCP", "")
    mcp_include = os.getenv("MCP_INCLUDE_DRIVE", "")
    print(f"DRIVE_MOCK={drive_mock!r}")
    print(f"GOOGLE_SERVICE_ACCOUNT_JSON={_mask_path(sa_path)}")
    print(f"AGENT_USE_MCP={agent_use_mcp!r}")
    print(f"MCP_INCLUDE_DRIVE={mcp_include!r}")
    print(f"Python={sys.version.split()[0]}")
    print(f"cwd={os.getcwd()}")

    exists = bool(sa_path and Path(sa_path).is_file())
    print(f"SA JSON exists: {exists}")
    parsed = False
    client_email = None
    private_key_id = None
    if exists:
        data = json.loads(Path(sa_path).read_text(encoding="utf-8"))
        parsed = True
        client_email = data.get("client_email")
        private_key_id = data.get("private_key_id")
        print(f"JSON parsed: {parsed}")
        print(f"client_email: {client_email}")
        print(f"private_key_id present: {bool(private_key_id)}")
        print(f"token_uri: {data.get('token_uri')}")
    else:
        print("JSON parsed: False")

    return {
        "drive_mock": drive_mock,
        "sa_exists": exists,
        "parsed": parsed,
        "client_email": client_email,
        "private_key_id_present": bool(private_key_id),
    }


def step2_auth() -> dict:
    print("\n=== STEP 2 — Google authentication only ===")
    path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    print("Authentication started...")
    t0 = time.perf_counter()
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(
            path, scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        creds.refresh(Request())
        elapsed = time.perf_counter() - t0
        print(f"Authentication completed in {elapsed:.2f} seconds")
        print(f"Token valid: {bool(creds.token) and creds.valid}")
        return {"ok": True, "auth_s": elapsed, "creds": creds}
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        print(f"Authentication FAILED after {elapsed:.2f}s: {exc}")
        traceback.print_exc()
        return {"ok": False, "auth_s": elapsed, "error": str(exc)}


def step3_drive_client_direct(creds) -> dict:
    print("\n=== STEP 3 — Drive client directly (files().list pageSize=1) ===")
    from googleapiclient.discovery import build

    t_auth0 = time.perf_counter()
    # creds already refreshed in step 2; measure build + first call split
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    # Force token on wire via about first if needed — here measure list only
    t_auth1 = time.perf_counter()
    t_api0 = time.perf_counter()
    try:
        resp = (
            service.files()
            .list(pageSize=1, fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True)
            .execute()
        )
        t_api1 = time.perf_counter()
        auth_ms = (t_auth1 - t_auth0) * 1000
        api_ms = (t_api1 - t_api0) * 1000
        total_ms = (t_api1 - t_auth0) * 1000
        print(f"authentication/build time: {auth_ms:.1f} ms")
        print(f"API request time: {api_ms:.1f} ms")
        print(f"total time: {total_ms:.1f} ms")
        print(f"files returned: {len(resp.get('files', []))}")
        print(f"sample: {resp.get('files', [])[:1]}")
        return {"ok": True, "auth_ms": auth_ms, "api_ms": api_ms, "total_ms": total_ms, "service": service}
    except Exception as exc:
        t_api1 = time.perf_counter()
        print(f"Drive list FAILED after {(t_api1 - t_auth0) * 1000:.1f} ms: {exc}")
        traceback.print_exc()
        return {"ok": False, "error": str(exc)}


def step6_tenant() -> dict:
    print("\n=== STEP 6 — Tenant configuration ===")
    from infrastructure.db.supabase_client import get_supabase_client

    t0 = time.perf_counter()
    client = get_supabase_client()
    row = client.table("tenants").select("id, drive_folder_id").eq("id", TENANT_ID).limit(1).execute()
    elapsed_ms = (time.perf_counter() - t0) * 1000
    data = (row.data or [{}])[0]
    folder_id = data.get("drive_folder_id")
    print(f"tenant_id={TENANT_ID}")
    print(f"drive_folder_id={folder_id!r}")
    print(f"tenant lookup: {elapsed_ms:.1f} ms")

    issues = []
    if folder_id is None:
        issues.append("drive_folder_id is None")
    elif folder_id == "":
        issues.append("drive_folder_id is empty string")
    elif folder_id in PLACEHOLDER_FOLDER_IDS:
        issues.append(f"drive_folder_id is seed PLACEHOLDER: {folder_id}")
    elif str(folder_id).startswith("drive-folder-"):
        issues.append(f"drive_folder_id looks like demo placeholder: {folder_id}")

    if issues:
        for i in issues:
            print(f"INVALID: {i}")
    else:
        print("drive_folder_id looks like a real Google folder id (non-placeholder)")

    return {
        "tenant_id": TENANT_ID,
        "drive_folder_id": folder_id,
        "issues": issues,
        "lookup_ms": elapsed_ms,
    }


def _list_children(service, folder_id: str, *, page_size: int = 20, q_extra: str | None = None):
    q = f"'{folder_id}' in parents and trashed = false"
    if q_extra:
        q = f"{q} and {q_extra}"
    print(f"Drive query: {q}")
    t0 = time.perf_counter()
    resp = (
        service.files()
        .list(
            q=q,
            pageSize=page_size,
            fields="files(id, name, mimeType, parents, webViewLink)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000
    files = resp.get("files", [])
    print(f"list elapsed: {elapsed_ms:.1f} ms, count={len(files)}")
    return files, elapsed_ms, q


def step7_folder_structure(service, root_id: str) -> dict:
    print("\n=== STEP 7 — Google Drive structure (root children) ===")
    try:
        files, elapsed_ms, q = _list_children(service, root_id, page_size=50)
    except Exception as exc:
        print(f"FAILED listing root children: {exc}")
        traceback.print_exc()
        return {"ok": False, "error": str(exc)}

    for f in files:
        print(f"  name={f.get('name')!r} id={f.get('id')} mime={f.get('mimeType')}")

    folder_mime = "application/vnd.google-apps.folder"
    names = { (f.get("name") or "").lower(): f for f in files if f.get("mimeType") == folder_mime }
    required = ["papers", "textbooks", "syllabus"]
    present = {n: n in names for n in required}
    for n in required:
        print(f"required '{n}': {'FOUND' if present[n] else 'MISSING'}" + (f" id={names[n]['id']}" if present[n] else ""))

    return {
        "ok": True,
        "children": files,
        "present": present,
        "papers_id": names["papers"]["id"] if present.get("papers") else None,
        "elapsed_ms": elapsed_ms,
        "query": q,
    }


def step8_papers(service, papers_id: str | None) -> dict:
    print("\n=== STEP 8 — papers/ folder contents ===")
    if not papers_id:
        print("SKIP: papers folder id unknown")
        return {"ok": False, "error": "papers folder missing"}
    try:
        files, elapsed_ms, q = _list_children(service, papers_id, page_size=20)
    except Exception as exc:
        print(f"FAILED listing papers: {exc}")
        traceback.print_exc()
        return {"ok": False, "error": str(exc)}

    for f in files:
        print(
            f"  filename={f.get('name')!r} mime={f.get('mimeType')} id={f.get('id')} "
            f"parents={f.get('parents')} webViewLink={f.get('webViewLink')}"
        )
    if not files:
        print("ZERO files — possible causes: empty folder | wrong parent id | permission (SA cannot see files)")
    return {"ok": True, "files": files, "elapsed_ms": elapsed_ms, "query": q}


def step9_search_query(service, papers_id: str | None, query: str) -> dict:
    print("\n=== STEP 9 — Exact search query (app logic) ===")
    if not papers_id:
        print("SKIP: no papers_id")
        return {"ok": False}
    tokens = [t.replace("'", "\\'") for t in query.split() if len(t) > 2]
    search_term = max(tokens, key=len) if tokens else query.replace("'", "\\'")
    q = f"'{papers_id}' in parents and trashed = false and name contains '{search_term}'"
    print(f"Complete query string: {q}")
    t0 = time.perf_counter()
    try:
        resp = (
            service.files()
            .list(
                q=q,
                pageSize=5,
                fields="files(id, name, mimeType, webViewLink)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        files = resp.get("files", [])
        print(f"search elapsed: {elapsed_ms:.1f} ms, count={len(files)}")
        for f in files:
            print(f"  {f.get('name')} -> {f.get('webViewLink')}")
        return {"ok": True, "query": q, "files": files, "elapsed_ms": elapsed_ms}
    except Exception as exc:
        print(f"Search FAILED: {exc}")
        traceback.print_exc()
        return {"ok": False, "query": q, "error": str(exc)}


def step5_and_10_drive_tool() -> dict:
    print("\n=== STEP 5+10a — DriveTool.drive_search (no MCP) with stage timers ===")
    from agents.tools.drive_tool import DriveTool

    tool = DriveTool()
    t0 = time.perf_counter()
    raw = tool.drive_search(
        tenant_id=TENANT_ID,
        query=SEARCH_QUERY,
        folder="papers",
        class_ids=CLASS_IDS,
    )
    total_ms = (time.perf_counter() - t0) * 1000
    print(f"DriveTool total wall time: {total_ms:.1f} ms")
    print(f"DriveTool result: {raw[:500]}")
    return {"ok": True, "total_ms": total_ms, "result": raw}


async def step10b_mcp() -> dict:
    print("\n=== STEP 10b+11 — MCP drive_search ===")
    t_start = time.perf_counter()
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from mcp_servers.mcp_config import build_mcp_server_config, mcp_include_drive

        if not mcp_include_drive():
            print("MCP_INCLUDE_DRIVE is false — axiom-drive not in config")
            return {"ok": False, "error": "MCP_INCLUDE_DRIVE=false"}

        cfg = build_mcp_server_config()
        if "axiom-drive" not in cfg:
            print("axiom-drive missing from build_mcp_server_config()")
            return {"ok": False, "error": "axiom-drive not configured"}

        print(f"MCP server config keys: {list(cfg.keys())}")
        print("MCP server started (client connecting to axiom-drive)...")
        client = MultiServerMCPClient({"axiom-drive": cfg["axiom-drive"]})
        tools = await client.get_tools()
        startup_ms = (time.perf_counter() - t_start) * 1000
        names = [t.name for t in tools]
        print(f"MCP startup/list tools: {startup_ms:.1f} ms")
        print(f"Registered tools: {names}")
        print(f"drive_search present: {'drive_search' in names}")
        print(f"drive_list present: {'drive_list' in names}")

        search = next(t for t in tools if t.name == "drive_search")
        t_call = time.perf_counter()
        raw = await search.ainvoke(
            {
                "tenant_id": TENANT_ID,
                "query": SEARCH_QUERY,
                "folder": "papers",
                "class_ids": CLASS_IDS,
            }
        )
        call_ms = (time.perf_counter() - t_call) * 1000
        print(f"MCP drive_search call: {call_ms:.1f} ms")
        print(f"MCP result: {str(raw)[:500]}")
        print("MCP server stayed alive through tool call: True")
        return {
            "ok": True,
            "startup_ms": startup_ms,
            "call_ms": call_ms,
            "tools": names,
            "result": str(raw),
        }
    except Exception as exc:
        print(f"MCP FAILED: {exc}")
        traceback.print_exc()
        return {"ok": False, "error": str(exc)}


def step12_network() -> dict:
    print("\n=== STEP 12 — Network measurements ===")
    host = "oauth2.googleapis.com"
    t_dns0 = time.perf_counter()
    infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    dns_ms = (time.perf_counter() - t_dns0) * 1000
    print(f"DNS resolution {host}: {dns_ms:.1f} ms")
    results = []
    for fam, typ, proto, _canon, sockaddr in infos:
        s = socket.socket(fam, typ, proto)
        s.settimeout(5)
        t0 = time.perf_counter()
        try:
            s.connect(sockaddr)
            ms = (time.perf_counter() - t0) * 1000
            status = "OK"
        except Exception as exc:
            ms = (time.perf_counter() - t0) * 1000
            status = f"FAIL ({exc})"
        finally:
            s.close()
        fam_name = socket.AddressFamily(fam).name
        print(f"HTTPS connect {fam_name} {sockaddr}: {status} in {ms:.1f} ms")
        results.append({"family": fam_name, "addr": str(sockaddr), "status": status, "ms": ms})

    # Second auth timing (httplib2 path used by googleapiclient)
    path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    httplib2_ms = None
    requests_ms = None
    try:
        from google.oauth2 import service_account
        from google_auth_httplib2 import AuthorizedHttp
        import httplib2
        from googleapiclient.discovery import build

        creds = service_account.Credentials.from_service_account_file(
            path, scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        http = AuthorizedHttp(creds, http=httplib2.Http(timeout=60))
        t0 = time.perf_counter()
        build("drive", "v3", http=http, cache_discovery=False)
        # trigger token via about
        from google.auth.transport.requests import Request

        t1 = time.perf_counter()
        creds2 = service_account.Credentials.from_service_account_file(
            path, scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        creds2.refresh(Request())
        requests_ms = (time.perf_counter() - t1) * 1000
        print(f"OAuth refresh via requests: {requests_ms:.1f} ms")

        # httplib2 path: first authenticated request
        from googleapiclient.discovery import build as build2

        creds3 = service_account.Credentials.from_service_account_file(
            path, scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        svc = build2("drive", "v3", credentials=creds3, cache_discovery=False)
        t2 = time.perf_counter()
        try:
            svc.about().get(fields="user").execute()
            httplib2_ms = (time.perf_counter() - t2) * 1000
            print(f"OAuth+about via googleapiclient/httplib2: {httplib2_ms:.1f} ms")
        except Exception as exc:
            httplib2_ms = (time.perf_counter() - t2) * 1000
            print(f"OAuth+about via googleapiclient/httplib2 FAILED in {httplib2_ms:.1f} ms: {exc}")
    except Exception as exc:
        print(f"Network auth probes error: {exc}")
        traceback.print_exc()

    return {
        "dns_ms": dns_ms,
        "connects": results,
        "requests_refresh_ms": requests_ms,
        "httplib2_about_ms": httplib2_ms,
    }


def main() -> int:
    print(f"debug_drive_integration started at {datetime.now(timezone.utc).isoformat()}")
    report: dict = {"steps": {}}

    report["steps"]["1"] = step1_environment()
    if not report["steps"]["1"].get("sa_exists"):
        print("\nSTOP: SA JSON missing — cannot continue Google steps")
        _print_summary(report)
        return 1

    auth = step2_auth()
    report["steps"]["2"] = {k: v for k, v in auth.items() if k != "creds"}
    if not auth.get("ok"):
        print("\nSTOP: authentication failed")
        report["steps"]["12"] = step12_network()
        _print_summary(report)
        return 1

    direct = step3_drive_client_direct(auth["creds"])
    report["steps"]["3"] = {k: v for k, v in direct.items() if k != "service"}
    service = direct.get("service")

    tenant = step6_tenant()
    report["steps"]["6"] = tenant
    root_id = tenant.get("drive_folder_id")

    if service and root_id and not tenant.get("issues"):
        structure = step7_folder_structure(service, root_id)
        report["steps"]["7"] = {
            "ok": structure.get("ok"),
            "present": structure.get("present"),
            "papers_id": structure.get("papers_id"),
            "elapsed_ms": structure.get("elapsed_ms"),
            "error": structure.get("error"),
            "child_count": len(structure.get("children") or []),
        }
        papers = step8_papers(service, structure.get("papers_id"))
        report["steps"]["8"] = {
            "ok": papers.get("ok"),
            "file_count": len(papers.get("files") or []),
            "elapsed_ms": papers.get("elapsed_ms"),
            "error": papers.get("error"),
        }
        search = step9_search_query(service, structure.get("papers_id"), SEARCH_QUERY)
        report["steps"]["9"] = {
            "ok": search.get("ok"),
            "query": search.get("query"),
            "file_count": len(search.get("files") or []),
            "elapsed_ms": search.get("elapsed_ms"),
            "error": search.get("error"),
        }
    elif service and root_id and tenant.get("issues"):
        print("\n=== STEP 7/8/9 — attempting despite placeholder/invalid folder id ===")
        structure = step7_folder_structure(service, root_id)
        report["steps"]["7"] = {
            "ok": structure.get("ok"),
            "present": structure.get("present"),
            "error": structure.get("error"),
            "child_count": len(structure.get("children") or []),
        }
        report["steps"]["8"] = step8_papers(service, structure.get("papers_id"))
        report["steps"]["9"] = step9_search_query(service, structure.get("papers_id"), SEARCH_QUERY)
    else:
        print("\nSKIP steps 7–9: no service or no drive_folder_id")

    tool_result = step5_and_10_drive_tool()
    report["steps"]["5_10a"] = tool_result

    mcp_result = asyncio.run(step10b_mcp())
    report["steps"]["10b_11"] = mcp_result

    report["steps"]["12"] = step12_network()
    _print_summary(report)
    return 0


def _print_summary(report: dict) -> None:
    print("\n" + "=" * 60)
    print("STEP 13 — SUMMARY (raw evidence; see printed steps above)")
    print("=" * 60)
    print(json.dumps(report, indent=2, default=str)[:8000])


if __name__ == "__main__":
    raise SystemExit(main())
