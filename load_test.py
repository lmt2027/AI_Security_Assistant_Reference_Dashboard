
"""Create and benchmark a separate SQLite test database.

Never modifies the original security_assistant.db file.
"""

import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
SOURCE = PROJECT_DIR / "security_assistant.db"
TEST_DB = PROJECT_DIR / "security_assistant_load_test.db"

NUMBER_OF_EVENTS = 1000


def main():
    if not SOURCE.is_file():
        print("ERROR: Original database not found.")
        return

    if TEST_DB.exists():
        print(
            "ERROR: Load-test database already exists. "
            "Move or rename it before running again."
        )
        return

    started = time.perf_counter()

    # Use SQLite's backup API for a consistent database copy.
    with sqlite3.connect(
        f"{SOURCE.as_uri()}?mode=ro",
        uri=True,
    ) as source:
        with sqlite3.connect(TEST_DB) as destination:
            source.backup(destination)

    with sqlite3.connect(TEST_DB) as connection:
        schema = connection.execute(
            "PRAGMA table_info(security_events)"
        ).fetchall()

        columns = [row[1] for row in schema]

        expected = [
            "event_time",
            "event_type",
            "account",
            "source_ip",
            "outcome",
            "details",
        ]

        if not all(column in columns for column in expected):
            print("Database event schema differs from expected.")
            print("Actual columns:", columns)
            print("No load-test events were inserted.")
            return

        rows = []

        for i in range(NUMBER_OF_EVENTS):
            event_time = (
                datetime.now() - timedelta(minutes=i)
            ).isoformat(timespec="seconds")

            rows.append(
                (
                    event_time,
                    "failed_login",
                    f"load_test_user_{i % 50}",
                    f"192.0.2.{(i % 250) + 1}",
                    "failure",
                    "Synthetic load-testing event",
                )
            )

        insert_started = time.perf_counter()

        connection.executemany(
            """
            INSERT INTO security_events
            (
                event_time,
                event_type,
                account,
                source_ip,
                outcome,
                details
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

        connection.commit()

        insert_seconds = (
            time.perf_counter() - insert_started
        )

        query_started = time.perf_counter()

        total_events = connection.execute(
            "SELECT COUNT(*) FROM security_events"
        ).fetchone()[0]

        recent_events = connection.execute(
            """
            SELECT *
            FROM security_events
            ORDER BY id DESC
            LIMIT 1000
            """
        ).fetchall()

        query_seconds = (
            time.perf_counter() - query_started
        )

    total_seconds = time.perf_counter() - started

    print("\nLOAD TEST COMPLETED")
    print("-----------------------------")
    print(f"Events added: {NUMBER_OF_EVENTS}")
    print(f"Total events: {total_events}")
    print(f"Insert time: {insert_seconds:.3f} seconds")
    print(f"Query time: {query_seconds:.3f} seconds")
    print(f"Records retrieved: {len(recent_events)}")
    print(f"Total test time: {total_seconds:.3f} seconds")
    print(f"Test database: {TEST_DB.name}")
    print("Original database: UNCHANGED")


if __name__ == "__main__":
    main()
