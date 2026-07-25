from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from models.school import School


schools = Blueprint(
    "schools",
    __name__,
)


@schools.get("/api/schools/search")
def search_schools():
    query = request.args.get(
        "q",
        "",
    ).strip()

    if len(query) < 2:
        return jsonify([])

    matches = (
        School.query
        .filter(
            School.is_active.is_(True),
            or_(
                School.school_name.ilike(
                    f"%{query}%"
                ),
                School.short_name.ilike(
                    f"%{query}%"
                ),
            ),
        )
        .order_by(
            School.school_name.asc()
        )
        .limit(20)
        .all()
    )

    return jsonify(
        [
            {
                "id": school.id,
                "name": school.school_name,
                "short_name": school.short_name,
                "school_type": school.school_type,
                "sector": school.sector,
                "region": school.region,
                "province": school.province,
                "city": school.city,
            }
            for school in matches
        ]
    )
