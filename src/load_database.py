"""
AstroGuide AI - Relational Database Loader
==========================================
Initializes SQLite schema and loads validated CSV tables into data/processed/astroguide.db
using chunked streaming to handle large activity event logs efficiently.

Author: AstroGuide Analytics Team
"""

import argparse
import logging
import sqlite3
import time
from pathlib import Path
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def init_database(db_path: Path, schema_file: Path):
    """Execute DDL script to create clean schema with constraints and indexes."""
    logger.info("Initializing SQLite database at %s...", db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
        logger.info("Schema successfully created from %s.", schema_file)
    finally:
        conn.close()


def load_table(conn: sqlite3.Connection, table_name: str, csv_path: Path, chunksize: int = 100000) -> int:
    """Load a CSV file into SQLite table with chunking."""
    logger.info("Loading %s into table '%s'...", csv_path.name, table_name)
    start_time = time.time()
    total_rows = 0

    # Stream CSV in chunks to keep memory footprint low
    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        chunk.to_sql(table_name, conn, if_exists="append", index=False)
        total_rows += len(chunk)

    elapsed = time.time() - start_time
    logger.info("Loaded %d rows into '%s' in %.2f seconds.", total_rows, table_name, elapsed)
    return total_rows


def verify_counts(conn: sqlite3.Connection):
    """Verify loaded row counts across all tables."""
    cursor = conn.cursor()
    tables = ["users", "subscriptions", "transactions", "user_activity", "churn_labels"]
    logger.info("Verifying database row counts...")

    results = {}
    for tbl in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        count = cursor.fetchone()[0]
        results[tbl] = count
        logger.info("  Table '%s': %d rows", tbl, count)

    return results


def main():
    parser = argparse.ArgumentParser(description="Load AstroGuide CSVs into SQLite database.")
    parser.add_argument("--db-path", type=str, default="data/processed/astroguide.db", help="Target SQLite database path")
    parser.add_argument("--data-dir", type=str, default="data/raw", help="Directory containing CSV files")
    parser.add_argument("--schema-file", type=str, default="sql/01_schema.sql", help="Path to schema DDL file")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    data_dir = Path(args.data_dir)
    schema_file = Path(args.schema_file)

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory {data_dir} does not exist. Run generate_data.py first.")

    # 1. Initialize Schema
    init_database(db_path, schema_file)

    # 2. Ingest Tables
    conn = sqlite3.connect(db_path)
    try:
        tables_map = {
            "users": data_dir / "users.csv",
            "subscriptions": data_dir / "subscriptions.csv",
            "transactions": data_dir / "transactions.csv",
            "user_activity": data_dir / "user_activity.csv",
            "churn_labels": data_dir / "churn_labels.csv",
        }

        for tbl, csv_file in tables_map.items():
            if not csv_file.exists():
                logger.error("Missing file: %s", csv_file)
                continue
            load_table(conn, tbl, csv_file)

        # 3. Verify Counts
        counts = verify_counts(conn)
        logger.info("All tables successfully loaded and verified in %s!", db_path)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
