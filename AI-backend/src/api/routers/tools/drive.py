"""Debug REST — Drive tool (same surface as drive_server MCP)."""

from __future__ import annotations

import asyncio
import time

from fastapi import APIRouter, Depends

from agents.tools.drive_tool import DriveTool
from api.deps import get_drive_tool
from api.schemas import DriveListRequest, DriveResponse, DriveSearchRequest

router = APIRouter(prefix="/tools/drive", tags=["Tools — Drive"])


@router.post("/search", response_model=DriveResponse)
async def search(req: DriveSearchRequest, drive: DriveTool = Depends(get_drive_tool)) -> DriveResponse:
    t0 = time.perf_counter()
    raw = await asyncio.to_thread(
        drive.drive_search,
        tenant_id=req.tenant_id,
        query=req.query,
        folder=req.folder,
    )
    return DriveResponse(result=raw, latency_ms=int((time.perf_counter() - t0) * 1000))


@router.post("/list", response_model=DriveResponse)
async def list_files(req: DriveListRequest, drive: DriveTool = Depends(get_drive_tool)) -> DriveResponse:
    t0 = time.perf_counter()
    raw = await asyncio.to_thread(drive.drive_list, tenant_id=req.tenant_id, folder=req.folder)
    return DriveResponse(result=raw, latency_ms=int((time.perf_counter() - t0) * 1000))
