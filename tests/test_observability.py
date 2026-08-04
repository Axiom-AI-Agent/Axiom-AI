"""Observability helper tests."""

from infrastructure.observability import TraceContext, trace_context


def test_trace_context_tags_and_metadata():
    ctx = TraceContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        session_id="sess-1",
        user_id="stu-1",
    )
    assert "tenant:demo-physics" in ctx.tags()
    assert ctx.metadata()["tenant_id"] == "tenant-demo-physics"


def test_trace_context_noop_when_langfuse_disabled():
    ctx = TraceContext(tenant_id="tenant-demo-physics")
    with trace_context(ctx):
        assert True
