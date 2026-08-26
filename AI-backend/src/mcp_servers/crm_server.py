"""
CRM MCP Server — admissions + escalation actions.

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
    selected_class_id: str | None = None,
    clear_selected_class: bool = False,
) -> str:
    """Update student profile during onboarding (name, school, district, consent, class)."""
    return _init().register_student(
        tenant_id=tenant_id,
        phone=phone,
        student_id=student_id,
        name=name,
        school=school,
        district=district,
        consent=consent,
        selected_class_id=selected_class_id,
        clear_selected_class=clear_selected_class,
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
def get_tenant_info(tenant_id: str) -> str:
    """Fetch tuition centre profile, open classes, and staff summary."""
    return _init().get_tenant_info(tenant_id=tenant_id)


@mcp.tool()
def get_class_details(
    tenant_id: str,
    class_id: str | None = None,
    class_name: str | None = None,
    subject: str | None = None,
    grade: str | None = None,
) -> str:
    """Look up one or more classes by id, name, subject, or grade."""
    return _init().get_class_details(
        tenant_id=tenant_id,
        class_id=class_id,
        class_name=class_name,
        subject=subject,
        grade=grade,
    )


@mcp.tool()
def list_staff(tenant_id: str, role: str | None = None) -> str:
    """List staff/tutors for a tenant, optionally filtered by role."""
    return _init().list_staff(tenant_id=tenant_id, role=role)


@mcp.tool()
def commit_onboarding(
    tenant_id: str,
    phone: str,
    name: str,
    school: str,
    district: str,
    class_id: str,
    language_pref: str | None = None,
) -> str:
    """Create student profile and pending enrollment after explicit confirmation."""
    return _init().commit_onboarding(
        tenant_id=tenant_id,
        phone=phone,
        name=name,
        school=school,
        district=district,
        class_id=class_id,
        language_pref=language_pref,
    )


@mcp.tool()
def create_enrollment(tenant_id: str, student_id: str, class_id: str) -> str:
    """Enroll a student in a class (requires PDPA consent)."""
    return _init().create_enrollment(
        tenant_id=tenant_id,
        student_id=student_id,
        class_id=class_id,
    )


@mcp.tool()
def create_escalation(
    tenant_id: str,
    student_id: str,
    reason_code: str,
    media_url: str | None = None,
    student_message: str | None = None,
    enrollment_id: str | None = None,
) -> str:
    """Open a dashboard escalation (payment receipt or talk-to-tutor)."""
    return _init().create_escalation(
        tenant_id=tenant_id,
        student_id=student_id,
        reason_code=reason_code,
        media_url=media_url,
        student_message=student_message,
        enrollment_id=enrollment_id,
    )


@mcp.tool()
def resolve_escalation(tenant_id: str, escalation_id: str) -> str:
    """Staff resolves escalation — payment activates enrollment; tutor closes ticket."""
    return _init().resolve_escalation(
        tenant_id=tenant_id,
        escalation_id=escalation_id,
    )


@mcp.tool()
def reject_payment_escalation(
    tenant_id: str,
    escalation_id: str,
    reviewed_by: str | None = None,
) -> str:
    """Staff rejects payment receipt — closes escalation without enrollment."""
    return _init().reject_payment_escalation(
        tenant_id=tenant_id,
        escalation_id=escalation_id,
        reviewed_by=reviewed_by,
    )


@mcp.tool()
def submit_payment_receipt(
    tenant_id: str,
    student_id: str,
    image_ref: str,
) -> str:
    """Legacy alias — creates payment_receipt escalation."""
    return _init().submit_payment_receipt(
        tenant_id=tenant_id,
        student_id=student_id,
        image_ref=image_ref,
    )


@mcp.tool()
def resolve_enrollment_escalation(tenant_id: str, escalation_id: str) -> str:
    """Staff approves payment review — activates enrollment."""
    return _init().resolve_enrollment_escalation(
        tenant_id=tenant_id,
        escalation_id=escalation_id,
    )


if __name__ == "__main__":
    logger.info("Starting axiom-crm MCP server on stdio...")
    mcp.run()
