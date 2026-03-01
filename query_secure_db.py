import sqlite3
import os

db_path = r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\data\secure.db"
if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    print(f"Tables: {tables}")

    for table_tuple in tables:
        table = table_tuple[0]
        print(f"\n--- Table: {table} ---")
        cursor.execute(f"SELECT * FROM {table} LIMIT 10")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
