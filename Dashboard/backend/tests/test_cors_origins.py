import re

from app.cors import (
    DEFAULT_ORIGIN_REGEX,
    DEFAULT_PRODUCTION_ORIGIN,
    build_cors_origins,
)


def test_build_cors_origins_includes_vercel_production():
    origins = build_cors_origins(frontend_url="", cors_origins="")
    assert DEFAULT_PRODUCTION_ORIGIN in origins
    assert "http://localhost:3000" in origins


def test_build_cors_origins_strips_trailing_slash_and_splits():
    origins = build_cors_origins(
        frontend_url="https://axiom-dashboard-xi.vercel.app/",
        cors_origins="https://preview.example.com, https://custom.axiom.lk/",
    )
    assert "https://axiom-dashboard-xi.vercel.app" in origins
    assert "https://preview.example.com" in origins
    assert "https://custom.axiom.lk" in origins
    assert "https://axiom-dashboard-xi.vercel.app/" not in origins


def test_vercel_preview_origin_matches_default_regex():
    pattern = re.compile(DEFAULT_ORIGIN_REGEX)
    assert pattern.fullmatch("https://axiom-dashboard-xi.vercel.app")
    assert pattern.fullmatch("https://axiom-dashboard-git-main-team.vercel.app")
    assert not pattern.fullmatch("http://localhost:3000")
