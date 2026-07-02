"""Verify all Step 1 module imports are clean."""
import sys
import os

sys.path.insert(0, "c:/eMpulse/backend")
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"
os.environ["SECRET_KEY"] = "test-secret-key-for-import-verification"

from app.core.config import settings
print(f"OK: config.py | env={settings.app_env} | pool={settings.db_pool_size}")

from app.database.database import Base, engine
print(f"OK: database.py | engine class={engine.__class__.__name__}")

from app.database.session import get_db_session, AsyncSessionFactory
print(f"OK: session.py | factory class={AsyncSessionFactory.__class__.__name__}")

from app.database.base import Base as AlembicBase
print(f"OK: base.py | registered tables={list(AlembicBase.metadata.tables.keys())}")

from app.core.logging import configure_logging, JSONFormatter
print("OK: logging.py | JSONFormatter ready")

print()
print("=== ALL STEP 1 IMPORTS VERIFIED ===")
print(f"  App Name : {settings.app_name}")
print(f"  Env      : {settings.app_env}")
print(f"  Pool     : {settings.db_pool_size} / {settings.db_max_overflow}")
url_ok = settings.database_url.startswith("postgresql+asyncpg://")
print(f"  URL OK   : {url_ok}")
