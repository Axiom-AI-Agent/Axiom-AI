import os

DEFAULT_PRODUCTION_ORIGIN = "https://axiom-dashboard-xi.vercel.app"
DEFAULT_ORIGIN_REGEX = r"https://axiom-dashboard(-[a-z0-9]+)*\.vercel\.app"


def build_cors_origins(
    frontend_url: str | None = None,
    cors_origins: str | None = None,
) -> list[str]:
    """Explicit origins for credentialed CORS (wildcard is invalid with credentials)."""
    origins = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        DEFAULT_PRODUCTION_ORIGIN,
    }
    for raw in (
        frontend_url if frontend_url is not None else os.getenv("FRONTEND_URL", ""),
        cors_origins if cors_origins is not None else os.getenv("CORS_ORIGINS", ""),
    ):
        for part in raw.split(","):
            origin = part.strip().rstrip("/")
            if origin:
                origins.add(origin)
    return sorted(origins)


def cors_origin_regex() -> str:
    return os.getenv("CORS_ORIGIN_REGEX", DEFAULT_ORIGIN_REGEX)
