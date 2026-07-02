"""
tools/introspect_schema.py

Connects to the deployed Supabase PostgreSQL database and dumps the EXACT schema
— every table, column, type, nullable flag, default, primary key, and foreign key.

This output is the authoritative source used to generate SQLAlchemy models.

Usage:
    Set DATABASE_URL in .env, then run:
    python tools/introspect_schema.py

Output:
    Prints full schema to stdout AND writes to tools/schema_dump.json
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Ensure app is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env")
    sys.exit(1)

import asyncpg


SCHEMA_QUERY = """
SELECT
    t.table_name,
    c.column_name,
    c.ordinal_position,
    c.data_type,
    c.udt_name,
    c.character_maximum_length,
    c.numeric_precision,
    c.numeric_scale,
    c.is_nullable,
    c.column_default,
    c.is_identity,
    c.identity_generation
FROM information_schema.tables t
JOIN information_schema.columns c
    ON t.table_name = c.table_name
    AND t.table_schema = c.table_schema
WHERE t.table_schema = 'public'
  AND t.table_type = 'BASE TABLE'
ORDER BY t.table_name, c.ordinal_position;
"""

PK_QUERY = """
SELECT
    tc.table_name,
    kcu.column_name,
    tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.ordinal_position;
"""

FK_QUERY = """
SELECT
    tc.table_name          AS from_table,
    kcu.column_name        AS from_column,
    ccu.table_name         AS to_table,
    ccu.column_name        AS to_column,
    tc.constraint_name,
    rc.delete_rule,
    rc.update_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;
"""

UNIQUE_QUERY = """
SELECT
    tc.table_name,
    kcu.column_name,
    tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'UNIQUE'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;
"""

INDEX_QUERY = """
SELECT
    t.relname        AS table_name,
    i.relname        AS index_name,
    ix.indisunique   AS is_unique,
    array_agg(a.attname ORDER BY a.attnum) AS columns
FROM pg_class t
JOIN pg_index ix ON t.oid = ix.indrelid
JOIN pg_class i  ON i.oid = ix.indexrelid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
JOIN pg_namespace n ON n.oid = t.relnamespace
WHERE n.nspname = 'public'
  AND t.relkind = 'r'
GROUP BY t.relname, i.relname, ix.indisunique
ORDER BY t.relname, i.relname;
"""

ENUM_QUERY = """
SELECT
    t.typname    AS enum_name,
    e.enumlabel  AS enum_value,
    e.enumsortorder AS sort_order
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
JOIN pg_namespace n ON n.oid = t.typnamespace
WHERE n.nspname = 'public'
ORDER BY t.typname, e.enumsortorder;
"""


async def introspect(url: str) -> dict:
    """Connect to Supabase and collect full schema metadata."""

    # asyncpg uses a different URL format (no +asyncpg prefix)
    pg_url = url.replace("postgresql+asyncpg://", "postgresql://")

    print(f"Connecting to database...")
    conn = await asyncpg.connect(pg_url)

    try:
        print("Reading columns...")
        columns_raw = await conn.fetch(SCHEMA_QUERY)

        print("Reading primary keys...")
        pks_raw = await conn.fetch(PK_QUERY)

        print("Reading foreign keys...")
        fks_raw = await conn.fetch(FK_QUERY)

        print("Reading unique constraints...")
        uniques_raw = await conn.fetch(UNIQUE_QUERY)

        print("Reading indexes...")
        indexes_raw = await conn.fetch(INDEX_QUERY)

        print("Reading enums...")
        enums_raw = await conn.fetch(ENUM_QUERY)

    finally:
        await conn.close()

    # ---------------------------------------------------------------
    # Build structured output
    # ---------------------------------------------------------------

    # Primary keys: {table_name: [col, ...]}
    pk_map: dict[str, list[str]] = {}
    for row in pks_raw:
        pk_map.setdefault(row["table_name"], []).append(row["column_name"])

    # Unique constraints: {table_name: [col, ...]}
    unique_map: dict[str, list[str]] = {}
    for row in uniques_raw:
        unique_map.setdefault(row["table_name"], []).append(row["column_name"])

    # Foreign keys: list of dicts
    fk_list = [
        {
            "from_table": row["from_table"],
            "from_column": row["from_column"],
            "to_table": row["to_table"],
            "to_column": row["to_column"],
            "constraint_name": row["constraint_name"],
            "on_delete": row["delete_rule"],
            "on_update": row["update_rule"],
        }
        for row in fks_raw
    ]

    # Indexes
    index_list = [
        {
            "table": row["table_name"],
            "index": row["index_name"],
            "unique": row["is_unique"],
            "columns": list(row["columns"]),
        }
        for row in indexes_raw
    ]

    # Enums: {enum_name: [value, ...]}
    enum_map: dict[str, list[str]] = {}
    for row in enums_raw:
        enum_map.setdefault(row["enum_name"], []).append(row["enum_value"])

    # Tables with columns
    tables: dict[str, dict] = {}
    for row in columns_raw:
        tbl = row["table_name"]
        if tbl not in tables:
            tables[tbl] = {
                "table_name": tbl,
                "primary_keys": pk_map.get(tbl, []),
                "unique_columns": unique_map.get(tbl, []),
                "columns": [],
            }
        tables[tbl]["columns"].append({
            "column_name": row["column_name"],
            "ordinal_position": row["ordinal_position"],
            "data_type": row["data_type"],
            "udt_name": row["udt_name"],        # e.g. "uuid", "text", custom enum name
            "max_length": row["character_maximum_length"],
            "numeric_precision": row["numeric_precision"],
            "numeric_scale": row["numeric_scale"],
            "is_nullable": row["is_nullable"] == "YES",
            "column_default": row["column_default"],
            "is_identity": row["is_identity"] == "YES",
        })

    schema = {
        "tables": tables,
        "foreign_keys": fk_list,
        "indexes": index_list,
        "enums": enum_map,
    }

    return schema


def print_schema(schema: dict) -> None:
    """Pretty-print the schema to stdout for review."""

    print("\n" + "=" * 70)
    print("DEPLOYED SUPABASE SCHEMA — AUTHORITATIVE SOURCE OF TRUTH")
    print("=" * 70)

    print(f"\nENUMS ({len(schema['enums'])}):")
    for enum_name, values in schema["enums"].items():
        print(f"  {enum_name}: {values}")

    print(f"\nTABLES ({len(schema['tables'])}):")
    for tbl_name, tbl in schema["tables"].items():
        print(f"\n  TABLE: {tbl_name}")
        print(f"  PKs: {tbl['primary_keys']}")
        print(f"  Unique: {tbl['unique_columns']}")
        print(f"  Columns:")
        for col in tbl["columns"]:
            nullable = "NULL" if col["is_nullable"] else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col["column_default"] else ""
            print(f"    {col['column_name']:35s} {col['udt_name']:20s} {nullable}{default}")

    print(f"\nFOREIGN KEYS ({len(schema['foreign_keys'])}):")
    for fk in schema["foreign_keys"]:
        print(f"  {fk['from_table']}.{fk['from_column']} -> {fk['to_table']}.{fk['to_column']} (ON DELETE {fk['on_delete']})")

    print("\n" + "=" * 70)
    print(f"Total tables: {len(schema['tables'])}")
    print(f"Total FKs:    {len(schema['foreign_keys'])}")
    print(f"Total enums:  {len(schema['enums'])}")
    print("=" * 70 + "\n")


async def main():
    schema = await introspect(DATABASE_URL)

    # Print to stdout
    print_schema(schema)

    # Write JSON dump
    out_path = Path(__file__).parent / "schema_dump.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, default=str)

    print(f"Schema dump written to: {out_path}")
    print("\nShare schema_dump.json to generate exact SQLAlchemy models.")


if __name__ == "__main__":
    asyncio.run(main())
