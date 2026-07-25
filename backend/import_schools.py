"""Import or update schools from a CSV file."""

import argparse
import csv
from pathlib import Path

from app import app
from extensions import db
from models.school import School


SUPPORTED_FIELDS = (
    "short_name",
    "school_type",
    "sector",
    "region",
    "province",
    "city",
    "website",
)


def clean(value):
    if value is None:
        return None

    value = value.strip()

    return value or None


def parse_active(value):
    if value is None or not value.strip():
        return True

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "active",
    }


def find_existing_school(
    source,
    official_code,
    school_name,
    city,
):
    if official_code:
        existing = School.query.filter_by(
            directory_source=source,
            official_school_code=official_code,
        ).first()

        if existing:
            return existing

    return School.query.filter_by(
        directory_source=source,
        school_name=school_name,
        city=city,
    ).first()


def import_schools(
    csv_path,
    default_source,
):
    added = 0
    updated = 0
    skipped = 0

    with csv_path.open(
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if not reader.fieldnames:
            raise ValueError(
                "The CSV file has no header row."
            )

        if "school_name" not in reader.fieldnames:
            raise ValueError(
                "The CSV must contain a school_name column."
            )

        for line_number, row in enumerate(
            reader,
            start=2,
        ):
            school_name = clean(
                row.get("school_name")
            )

            if not school_name:
                print(
                    f"Skipping line {line_number}: "
                    "missing school_name."
                )
                skipped += 1
                continue

            source = (
                clean(row.get("directory_source"))
                or default_source
            )

            official_code = clean(
                row.get("official_school_code")
                or row.get("school_code")
                or row.get("hei_code")
                or row.get("school_id")
            )

            city = clean(
                row.get("city")
            )

            school = find_existing_school(
                source=source,
                official_code=official_code,
                school_name=school_name,
                city=city,
            )

            is_new = school is None

            if is_new:
                school = School()
                db.session.add(school)

            school.school_name = school_name
            school.directory_source = source
            school.official_school_code = (
                official_code
            )
            school.is_active = parse_active(
                row.get("is_active")
            )

            for field in SUPPORTED_FIELDS:
                value = clean(
                    row.get(field)
                )

                if value is not None:
                    setattr(
                        school,
                        field,
                        value,
                    )

            latitude = clean(
                row.get("latitude")
            )
            longitude = clean(
                row.get("longitude")
            )

            if latitude is not None:
                school.latitude = float(latitude)

            if longitude is not None:
                school.longitude = float(longitude)

            if is_new:
                added += 1
            else:
                updated += 1

    db.session.commit()

    return {
        "added": added,
        "updated": updated,
        "skipped": skipped,
    }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Import schools into StudExEl."
        )
    )

    parser.add_argument(
        "csv_path",
        type=Path,
        help="Path to the school CSV file.",
    )

    parser.add_argument(
        "--source",
        default="MANUAL",
        help=(
            "Default directory source, "
            "such as CHED or DEPED."
        ),
    )

    arguments = parser.parse_args()

    if not arguments.csv_path.is_file():
        raise SystemExit(
            f"CSV file not found: "
            f"{arguments.csv_path}"
        )

    with app.app_context():
        result = import_schools(
            csv_path=arguments.csv_path,
            default_source=(
                arguments.source.strip().upper()
            ),
        )

    print(
        "School import completed: "
        f"{result['added']} added, "
        f"{result['updated']} updated, "
        f"{result['skipped']} skipped."
    )


if __name__ == "__main__":
    main()
