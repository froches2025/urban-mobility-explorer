"""
seed_db.py - Create the tables from schema.sql and load the cleaned data.

Run AFTER scripts/clean_data.py:
    python seed_db.py

    choose the database with the DB_URL environment variable.
        SQLite (default, no setup needed):
             python seed_db.py
        MySQL (the database must already exist):
           export DB_URL="mysql+pymysql://user:password@localhost/mobility"
           python seed_db.py
    """
import os  
from pathlib import Path 

import pandas as pd 
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve(). parent
CLEAN_DIR = BASE_DIR / "clean_data"
SCHEMA_FILE = BASE_DIR / "schema.sql"
DB_URL = os.environ.get("DB_URL", f"sqlite:///{BASE_DIR / 'mobility.db'}")

CHUNK_SIZE = 50_000


def run_schema(engine):
    lines = [
        line for line in SCHEMA_FILE.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("--")
    ]
    statements = [s.strip() for s in "\n".join(lines).split(";") if s.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
    print(f"created tables and indexes ({len(statements)} statements)")


def load_table(engine, table, csv_name, date_columns=None):
    path = CLEAN_DIR / csv_name
    if not path.exists():
        raise SystemExit(f"{path} not found. Run scripts/clean_data.py first.")
    total = 0
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, parse_dates=date_columns or []):
        chunk.to_sql(table, engine, if_exists="append", index=False)
        total += len(chunk)
    print(f"Loaded {total:,} rows into {table}")


def main():
    engine = create_engine(DB_URL)
    run_schema(engine)
    # parents first, because of the foreign keys
    load_table(engine, "boroughs", "boroughs_clean.csv")
    load_table(engine, "zones", "zones_clean.csv")
    load_table(
        engine,
        "trips",
        "trips_clean.csv",
        date_columns=["pickup_datetime", "dropoff_datetime"],
    )

    with engine.connect() as conn:
        for table in ["boroughs", "zones", "trips"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"{table}: {count:,} rows")

if __name__ == "__main__":
    main()
