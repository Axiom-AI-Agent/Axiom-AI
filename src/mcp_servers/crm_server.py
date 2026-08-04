"""
CRM MCP Server — admissions actions (register_student, get_student, list_classes, create_enrollment).

Adapted from Week 13 ``mcp_servers/crm_server.py`` for tenant-scoped Axiom MVP.
"""

from __future__ import annotations

import os
import sys

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from dotenv import load_dotenv

load_dotenv()

from loguru import logger
from mcp.server.fastmcp import FastMCP

from agents.tools.crm_tool import CrmTool

mcp = FastMCP("axiom-crm")
_tool: CrmTool | None = None


def _init() -> CrmTool:
    global _tool
    if _tool is None:
        logger.info("Initialising CRM MCP server...")
        _tool = CrmTool()
    return _tool


@mcp.tool()
def register_student(
    tenant_id: str,
    phone: str,
    student_id: str | None = None,
    name: str | None = None,
    school: str | None = None,
    district: str | None = None,
    consent: bool = False,
) -> str:
    """Update student profile during onboarding (name, school, district, consent)."""
    return _init().register_student(
        tenant_id=tenant_id,
        phone=phone,
        student_id=student_id,
        name=name,
        school=school,
        district=district,
        consent=consent,
    )


@mcp.tool()
def get_student(tenant_id: str, phone: str) -> str:
    """Fetch student profile and active enrollments by phone."""
    return _init().get_student(tenant_id=tenant_id, phone=phone)


@mcp.tool()
def list_classes(
    tenant_id: str,
    subject: str | None = None,
    grade: str | None = None,
) -> str:
    """List available classes for a tenant, optionally filtered by subject/grade."""
    return _init().list_classes(tenant_id=tenant_id, subject=subject, grade=grade)


@mcp.tool()
def create_enrollment(tenant_id: str, student_id: str, class_id: str) -> str:
    """Enroll a student in a class (requires PDPA consent)."""
    return _init().create_enrollment(
        tenant_id=tenant_id,
        student_id=student_id,
        class_id=class_id,
    )


@mcp.tool()
def submit_payment_receipt(
    tenant_id: str,
    student_id: str,
    image_ref: str,
) -> str:
    """Submit payment receipt for pending enrollment and open staff review escalation."""
    return _init().submit_payment_receipt(
        tenant_id=tenant_id,
        student_id=student_id,
        image_ref=image_ref,
    )


@mcp.tool()
def resolve_enrollment_escalation(tenant_id: str, escalation_id: str) -> str:
    """Staff resolves payment review — activates enrollment."""
    return _init().resolve_enrollment_escalation(
        tenant_id=tenant_id,
        escalation_id=escalation_id,
    )


if __name__ == "__main__":
    logger.info("Starting axiom-crm MCP server on stdio...")
    mcp.run()
