"""Markdown-aware chunking: heading sections, breadcrumbs, page attribution."""

from __future__ import annotations

from services.ingest_service.chunkers import _token_len, fixed_chunk, parent_child_chunk

_DOC = {
    "url": "upload://t/notes",
    "title": "Physics Notes",
    "lesson": "5",
    "class_id": "class-a",
    "source_type": "pdf",
    "document_id": "doc-test",
}


def _doc(content: str) -> list[dict]:
    return [{**_DOC, "content": content}]


def test_token_len_beats_char_estimate():
    """Real token counting, not the old chars/4 approximation."""
    assert _token_len("hello world") <= 4


class TestHeadingSections:
    def test_parents_follow_heading_boundaries(self):
        content = (
            "# Kinematics\n\n## Free Fall\n\nBodies accelerate downward.\n\n"
            "## Projectiles\n\nMotion is parabolic.\n"
        )
        _, parents = parent_child_chunk(_doc(content))
        paths = {p["heading_path"] for p in parents}
        assert "Kinematics > Free Fall" in paths
        assert "Kinematics > Projectiles" in paths

    def test_children_are_contextualized_with_breadcrumb(self):
        content = "# Kinematics\n\n## Free Fall\n\n" + "The value is 9.81 downward. " * 40
        children, _ = parent_child_chunk(_doc(content))
        assert children
        first = children[0]
        assert first["embed_text"].startswith("Kinematics > Free Fall")
        # The stored text stays clean for display and citation.
        assert not first["text"].startswith("Kinematics >")

    def test_long_breadcrumb_keeps_deepest_headings(self):
        """A verbose H1 must not crowd out the specific heading on every chunk."""
        long_title = "A Very Long Document Title That Goes On For Quite Some Time Indeed Really"
        content = f"# {long_title}\n\n## Free Fall\n\n" + "Gravity content here. " * 40
        _, parents = parent_child_chunk(_doc(content))
        trail = parents[-1]["heading_path"]
        assert len(trail) <= 80
        assert "Free Fall" in trail

    def test_document_without_headings_still_chunks(self):
        children, parents = parent_child_chunk(_doc("Plain prose with no headings. " * 100))
        assert children and parents
        assert parents[0]["heading_path"] == ""


class TestPageAttribution:
    def test_page_markers_become_metadata_and_leave_text(self):
        content = (
            "<!-- page:1 -->\n# Kinematics\n\n" + "Velocity content. " * 30 + "\n\n"
            "<!-- page:2 -->\n## Free Fall\n\n" + "Gravity content. " * 30
        )
        children, parents = parent_child_chunk(_doc(content))
        assert all("<!-- page:" not in c["text"] for c in children)
        assert all("<!-- page:" not in p["text"] for p in parents)
        assert {p["page_number"] for p in parents} == {1, 2}

    def test_fixed_chunk_also_strips_markers(self):
        chunks = fixed_chunk(_doc("<!-- page:3 -->\n" + "word " * 500))
        assert chunks
        assert all("<!-- page:" not in c["text"] for c in chunks)
        assert chunks[0]["page_number"] == 3


class TestChunkContract:
    def test_parent_child_links_and_strategies(self):
        children, parents = parent_child_chunk(_doc("Velocity is displacement over time. " * 200))
        assert children[0]["strategy"] == "child"
        assert parents[0]["strategy"] == "parent"
        parent_ids = {p["parent_id"] for p in parents}
        assert all(c["parent_id"] in parent_ids for c in children)

    def test_source_type_propagates(self):
        children, parents = parent_child_chunk(_doc("# H\n\n" + "body " * 200))
        assert children[0]["source_type"] == "pdf"
        assert parents[0]["source_type"] == "pdf"

    def test_tables_are_not_split_mid_row(self):
        table = "| Col A | Col B |\n| --- | --- |\n| one | two |\n| three | four |"
        content = f"# Data\n\nIntro paragraph.\n\n{table}\n\nAfter table."
        children, _ = parent_child_chunk(_doc(content))
        table_chunks = [c for c in children if "| Col A |" in c["text"]]
        assert table_chunks
        assert any("| three | four |" in c["text"] for c in table_chunks)
