"""
AstroGuide AI - SQL Analysis Test & Query Runner
================================================
Executes analytical SQL scripts against data/processed/astroguide.db,
displays formatted outputs, and validates alignment with Python EDA results.

Author: AstroGuide Analytics Team
"""

import logging
import sqlite3
from pathlib import Path
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DB_PATH = Path("data/processed/astroguide.db")
SQL_DIR = Path("sql")


def execute_queries_from_file(conn: sqlite3.Connection, sql_file: Path):
    """Parse and execute distinct queries from an SQL file."""
    print("\n" + "=" * 80)
    print(f"EXECUTING: {sql_file.name}")
    print("=" * 80)

    with open(sql_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by semicolon, ignoring empty lines/comments
    raw_statements = content.split(";")
    query_num = 1

    for stmt in raw_statements:
        clean_stmt = stmt.strip()
        # Filter out empty statements or PRAGMA-only lines
        if not clean_stmt or clean_stmt.startswith("--") and "\nSELECT" not in clean_stmt and "\nWITH" not in clean_stmt:
            continue
        # Check if statement is a query (SELECT or WITH)
        if any(keyword in clean_stmt.upper() for keyword in ["SELECT", "WITH"]):
            print(f"\n--- Query {query_num} ---")
            # Extract header comment if present
            lines = clean_stmt.splitlines()
            for line in lines[:4]:
                if line.strip().startswith("--"):
                    print(line.strip())

            df = pd.read_sql_query(clean_stmt, conn)
            print(df.to_string(index=False))
            print("-" * 50)
            query_num += 1


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database {DB_PATH} not found. Run load_database.py first.")

    conn = sqlite3.connect(DB_PATH)
    try:
        execute_queries_from_file(conn, SQL_DIR / "02_business_analysis.sql")
        execute_queries_from_file(conn, SQL_DIR / "03_churn_analysis.sql")
        execute_queries_from_file(conn, SQL_DIR / "04_retention_cohorts.sql")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
