import csv
import os
import sqlite3

# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
DATABASE_PATH = os.path.join(BASE_DIR, "studexel.db")
CSV_PATH = os.path.join(BASE_DIR, "schools.csv")

# -------------------------------------------------
# Connect to Database
# -------------------------------------------------

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

print("Connected to StudExEl database.")

# -------------------------------------------------
# Read CSV and Insert Schools
# -------------------------------------------------

added = 0
skipped = 0

with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:

    reader = csv.DictReader(csvfile)

    for row in reader:

        # Check if the school already exists
        cursor.execute(
            "SELECT id FROM schools WHERE school_name = ?",
            (row["school_name"],)
        )

        existing = cursor.fetchone()

        if existing:
            skipped += 1
            continue

        # Insert new school
        cursor.execute(
            """
            INSERT INTO schools
            (
                school_name,
                short_name,
                school_type,
                sector,
                region,
                province,
                city,
                website,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["school_name"],
                row["short_name"],
                row["school_type"],
                row["sector"],
                row["region"],
                row["province"],
                row["city"],
                row["website"],
                1,
            ),
        )

        added += 1

connection.commit()

print(f"Added: {added} school(s)")
print(f"Skipped: {skipped} duplicate(s)")

connection.close()

print("Done!")