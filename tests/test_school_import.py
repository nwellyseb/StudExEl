from extensions import db
from import_schools import import_schools
from models.school import School


def test_import_schools_adds_school(
    app,
    tmp_path,
):
    csv_path = tmp_path / "schools.csv"

    csv_path.write_text(
        (
            "school_name,official_school_code,"
            "short_name,region,city\n"
            "Example State University,"
            "CHED-001,ESU,Region I,Example City\n"
        ),
        encoding="utf-8",
    )

    result = import_schools(
        csv_path=csv_path,
        default_source="CHED",
    )

    school = db.session.execute(
        db.select(School).where(
            School.official_school_code
            == "CHED-001"
        )
    ).scalar_one()

    assert result == {
        "added": 1,
        "updated": 0,
        "skipped": 0,
    }

    assert school.school_name == (
        "Example State University"
    )
    assert school.directory_source == "CHED"
    assert school.short_name == "ESU"
    assert school.region == "Region I"
    assert school.city == "Example City"
    assert school.is_active is True


def test_import_schools_updates_by_official_code(
    app,
    tmp_path,
):
    first_csv = tmp_path / "first.csv"
    second_csv = tmp_path / "second.csv"

    first_csv.write_text(
        (
            "school_name,official_school_code,"
            "region,city\n"
            "Old University Name,"
            "CHED-002,Old Region,Old City\n"
        ),
        encoding="utf-8",
    )

    second_csv.write_text(
        (
            "school_name,official_school_code,"
            "region,city\n"
            "Updated University Name,"
            "CHED-002,Updated Region,Updated City\n"
        ),
        encoding="utf-8",
    )

    import_schools(
        csv_path=first_csv,
        default_source="CHED",
    )

    result = import_schools(
        csv_path=second_csv,
        default_source="CHED",
    )

    schools = db.session.execute(
        db.select(School).where(
            School.official_school_code
            == "CHED-002"
        )
    ).scalars().all()

    assert result == {
        "added": 0,
        "updated": 1,
        "skipped": 0,
    }

    assert len(schools) == 1
    assert schools[0].school_name == (
        "Updated University Name"
    )
    assert schools[0].region == (
        "Updated Region"
    )
    assert schools[0].city == (
        "Updated City"
    )


def test_import_schools_skips_missing_name(
    app,
    tmp_path,
):
    csv_path = tmp_path / "schools.csv"

    csv_path.write_text(
        (
            "school_name,official_school_code\n"
            ",CHED-003\n"
        ),
        encoding="utf-8",
    )

    result = import_schools(
        csv_path=csv_path,
        default_source="CHED",
    )

    assert result == {
        "added": 0,
        "updated": 0,
        "skipped": 1,
    }

    assert db.session.execute(
        db.select(School)
    ).scalars().all() == []


def test_import_schools_preserves_shared_codes(
    app,
    tmp_path,
):
    csv_path = tmp_path / "shared-codes.csv"

    csv_path.write_text(
        (
            "school_name,official_school_code,"
            "region,city\n"
            "First Shared Code College,"
            "14049,CAR,Baguio City\n"
            "Second Shared Code College,"
            "14049,CAR,Baguio City\n"
            "Third Shared Code College,"
            "14049,CAR,Baguio City\n"
        ),
        encoding="utf-8",
    )

    result = import_schools(
        csv_path=csv_path,
        default_source="CHED",
    )

    schools = db.session.execute(
        db.select(School)
        .where(
            School.directory_source == "CHED",
            School.official_school_code == "14049",
        )
        .order_by(
            School.school_name
        )
    ).scalars().all()

    assert result == {
        "added": 3,
        "updated": 0,
        "skipped": 0,
    }

    assert [
        school.school_name
        for school in schools
    ] == [
        "First Shared Code College",
        "Second Shared Code College",
        "Third Shared Code College",
    ]
