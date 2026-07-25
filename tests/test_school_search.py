from extensions import db
from models.school import School


def test_school_search_requires_two_characters(
    client,
):
    response = client.get(
        "/api/schools/search?q=S"
    )

    assert response.status_code == 200
    assert response.get_json() == []


def test_school_search_matches_full_name(
    client,
    school,
):
    response = client.get(
        "/api/schools/search?q=StudExEl"
    )

    assert response.status_code == 200

    results = response.get_json()

    assert len(results) == 1
    assert results[0]["id"] == school.id
    assert results[0]["name"] == school.school_name


def test_school_search_matches_short_name(
    client,
    school,
):
    response = client.get(
        "/api/schools/search?q=STU"
    )

    assert response.status_code == 200

    results = response.get_json()

    assert len(results) == 1
    assert results[0]["short_name"] == "STU"


def test_school_search_excludes_inactive_schools(
    app,
    client,
):
    inactive_school = School(
        school_name="Inactive Test College",
        short_name="ITC",
        school_type="College",
        sector="Private",
        region="Test Region",
        city="Test City",
        is_active=False,
    )

    db.session.add(inactive_school)
    db.session.commit()

    response = client.get(
        "/api/schools/search?q=Inactive"
    )

    assert response.status_code == 200
    assert response.get_json() == []


def test_school_search_matches_separated_words(
    app,
    client,
):
    school = School(
        school_name="STI College Ortigas-Cainta",
        official_school_code="04161",
        directory_source="CHED",
        school_type="Private",
        sector="Private",
        region="Region IV-A",
        address="Cainta, Rizal",
        is_active=True,
    )

    db.session.add(school)
    db.session.commit()

    response = client.get(
        "/api/schools/search",
        query_string={
            "q": "STI Ortigas Cainta",
        },
    )

    assert response.status_code == 200

    results = response.get_json()

    assert len(results) == 1
    assert results[0]["name"] == (
        "STI College Ortigas-Cainta"
    )
