import sqlite3
import csv
import json
import os

db_path = r'C:\Users\Quencher\.copilot\session-state\9e69fdf0-c4e4-436c-bcb7-e38ba827f811\session.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# Phase progress
cur = conn.execute('''
WITH latest AS (
    SELECT filepath, verdict, phase, priority, gap_description, inspected_at,
           ROW_NUMBER() OVER (PARTITION BY filepath ORDER BY inspected_at DESC) AS rn
    FROM file_inspection
)
SELECT
    COALESCE(phase, 'UNASSIGNED') AS phase,
    COUNT(*) AS files,
    SUM(CASE WHEN verdict = 'GENUINE' THEN 1 ELSE 0 END) AS genuine,
    SUM(CASE WHEN verdict = 'ASPIRATIONAL' THEN 1 ELSE 0 END) AS aspirational,
    SUM(CASE WHEN verdict = 'THEATER' THEN 1 ELSE 0 END) AS theater,
    SUM(CASE WHEN verdict = 'STUB' THEN 1 ELSE 0 END) AS stub,
    SUM(CASE WHEN verdict = 'BROKEN' THEN 1 ELSE 0 END) AS broken,
    ROUND(100.0 * SUM(CASE WHEN verdict = 'GENUINE' THEN 1 ELSE 0 END) / COUNT(*), 2) AS genuine_pct
FROM latest WHERE rn = 1
GROUP BY COALESCE(phase, 'UNASSIGNED')
ORDER BY phase
''')

os.makedirs('baseline', exist_ok=True)
with open('baseline/phase0_current_phase_progress.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['phase', 'files', 'genuine', 'aspirational', 'theater', 'stub', 'broken', 'genuine_pct'])
    rows = cur.fetchall()
    writer.writerows(rows)
    print('Phase progress exported:')
    for row in rows:
        print(f"  Phase {row[0]}: {row[1]} files, {row[7]}% genuine")

# High-priority gaps
cur = conn.execute('''
WITH latest AS (
    SELECT filepath, verdict, phase, priority, gap_description, inspected_at,
           ROW_NUMBER() OVER (PARTITION BY filepath ORDER BY inspected_at DESC) AS rn
    FROM file_inspection
)
SELECT filepath, COALESCE(phase, 'UNASSIGNED') AS phase, verdict, priority, gap_description, inspected_at
FROM latest WHERE rn = 1
  AND verdict IN ('BROKEN', 'THEATER', 'STUB')
  AND priority IN ('CRITICAL', 'HIGH')
ORDER BY CASE priority WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END, phase, filepath
''')

rows = cur.fetchall()
with open('baseline/phase0_high_priority_gaps.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['filepath', 'phase', 'verdict', 'priority', 'gap_description', 'inspected_at'])
    writer.writerows(rows)
print(f'\nHigh-priority gaps exported: {len(rows)} CRITICAL/HIGH gaps')

# Release readiness
cur = conn.execute('''
WITH latest AS (
    SELECT filepath, verdict, phase, priority, inspected_at,
           ROW_NUMBER() OVER (PARTITION BY filepath ORDER BY inspected_at DESC) AS rn
    FROM file_inspection
)
SELECT
    COUNT(*) AS total_files,
    SUM(CASE WHEN verdict = 'GENUINE' THEN 1 ELSE 0 END) AS genuine,
    SUM(CASE WHEN verdict = 'ASPIRATIONAL' THEN 1 ELSE 0 END) AS aspirational,
    SUM(CASE WHEN verdict IN ('BROKEN', 'THEATER', 'STUB') THEN 1 ELSE 0 END) AS unresolved_gap_files,
    SUM(CASE WHEN priority = 'CRITICAL' AND verdict IN ('BROKEN', 'THEATER', 'STUB') THEN 1 ELSE 0 END) AS critical_gaps,
    SUM(CASE WHEN priority = 'HIGH' AND verdict IN ('BROKEN', 'THEATER', 'STUB') THEN 1 ELSE 0 END) AS high_gaps,
    ROUND(100.0 * SUM(CASE WHEN verdict = 'GENUINE' THEN 1 ELSE 0 END) / COUNT(*), 2) AS genuine_pct,
    ROUND(100.0 * SUM(CASE WHEN verdict = 'ASPIRATIONAL' THEN 1 ELSE 0 END) / COUNT(*), 2) AS aspirational_pct
FROM latest WHERE rn = 1
''')

row = cur.fetchone()
data = dict(row)
with open('baseline/phase0_release_readiness_snapshot.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f'\nRelease readiness snapshot:')
print(f"  Total files: {data['total_files']}")
print(f"  Genuine: {data['genuine']} ({data['genuine_pct']}%)")
print(f"  Aspirational: {data['aspirational']} ({data['aspirational_pct']}%)")
print(f"  Unresolved gaps: {data['unresolved_gap_files']}")
print(f"  CRITICAL gaps: {data['critical_gaps']}")
print(f"  HIGH gaps: {data['high_gaps']}")
print('\nAll baseline files exported to baseline/ directory')
