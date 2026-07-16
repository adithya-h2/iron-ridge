"""Audit .env without printing secret values."""
from pathlib import Path

PLACEHOLDERS = (
    "change-me",
    "your-password",
    "your-n8n",
    "your-agent",
    "sk-...",
    "sk-ant",
    "xoxb-",
    "changeme",
    "[your",
)


def audit(name: str, val: str | None) -> str:
    if val is None or val == "":
        return "MISSING"
    v = val.strip().strip('"').strip("'")
    if any(p in v.lower() for p in PLACEHOLDERS):
        return "PLACEHOLDER"
    if name == "DATABASE_URL":
        return "SET" if v.startswith("postgresql+asyncpg://") and "@" in v else "INVALID FORMAT"
    if name == "N8N_WEBHOOK_BASE_URL":
        if "localhost" in v or "127.0.0.1" in v:
            return "INVALID FORMAT (localhost)"
        return "SET" if v.startswith("http") else "INVALID FORMAT"
    if name == "FEATURE_N8N_PUBLISH":
        return f"SET ({v.lower()})"
    if name in ("REDIS_URL", "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD") and not v:
        return "OPTIONAL / NOT SET"
    return "SET"


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def main() -> None:
    env = load_env(Path(".env"))
    keys = [
        "DATABASE_URL",
        "SECRET_KEY",
        "AGENT_API_KEY",
        "N8N_WEBHOOK_BASE_URL",
        "FEATURE_N8N_PUBLISH",
        "LLM_TIMEOUT_SECONDS",
        "N8N_TIMEOUT_SECONDS",
        "REDIS_URL",
        "SMTP_HOST",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "EMAIL_ENABLED",
        "OPENAI_API_KEY",
        "SLACK_BOT_TOKEN",
        "METRICS_ENABLED",
        "ALLOWED_ORIGINS",
        "APP_ENV",
    ]
    for key in keys:
        print(f"{key}: {audit(key, env.get(key))}")


if __name__ == "__main__":
    main()
