"""Verify all Step 2 models import cleanly and match deployed Supabase schema."""
import sys
import os
import json
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))
os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test"
)
os.environ["SECRET_KEY"] = "test-key"

# Load ground truth from schema dump
schema_path = BACKEND_ROOT / "tools" / "schema_dump.json"
with open(schema_path) as f:
    schema = json.load(f)

deployed_tables = set(schema["tables"].keys())

# Import all models via base.py
from app.database.base import Base
registered_tables = set(Base.metadata.tables.keys())

print("=" * 60)
print("STEP 2 VERIFICATION — SQLAlchemy vs Deployed Supabase Schema")
print("=" * 60)

print(f"\nDeployed tables  ({len(deployed_tables)}): {sorted(deployed_tables)}")
print(f"Registered tables ({len(registered_tables)}): {sorted(registered_tables)}")

missing_from_orm = deployed_tables - registered_tables
extra_in_orm = registered_tables - deployed_tables

if missing_from_orm:
    print(f"\nFAIL - Tables in Supabase but NOT in ORM: {missing_from_orm}")
else:
    print("\nOK: All deployed tables are registered in ORM")

if extra_in_orm:
    print(f"WARN - Tables in ORM but NOT in Supabase: {extra_in_orm}")
else:
    print("OK: No phantom tables in ORM")

# Per-table column verification
print("\n" + "-" * 60)
print("COLUMN VERIFICATION (deployed vs ORM)")
print("-" * 60)

all_ok = True
for tbl_name in sorted(deployed_tables):
    if tbl_name not in registered_tables:
        continue
    deployed_cols = {c["column_name"] for c in schema["tables"][tbl_name]["columns"]}
    orm_table = Base.metadata.tables[tbl_name]
    orm_cols = set(orm_table.columns.keys())

    missing = deployed_cols - orm_cols
    extra = orm_cols - deployed_cols
    if missing or extra:
        all_ok = False
        print(f"\nFAIL [{tbl_name}]")
        if missing:
            print(f"  Missing from ORM  : {missing}")
        if extra:
            print(f"  Extra in ORM      : {extra}")
    else:
        print(f"  OK [{tbl_name}] — {len(deployed_cols)} columns matched")

print("\n" + "=" * 60)
if all_ok and not missing_from_orm and not extra_in_orm:
    print("ALL CHECKS PASSED — ORM exactly mirrors deployed Supabase schema")
else:
    print("CHECKS FAILED — review mismatches above")
print("=" * 60)
