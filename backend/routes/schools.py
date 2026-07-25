"""School directory search routes."""

import re

from flask import Blueprint, jsonify, request
from sqlalchemy import and_, or_

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

    search_terms = re.findall(
        r"[A-Za-z0-9]+",
        query,
    )

    if not search_terms:
        return jsonify([])

    term_filters = [
        or_(
            School.school_name.ilike(
                f"%{term}%"
            ),
            School.short_name.ilike(
                f"%{term}%"
            ),
            School.region.ilike(
                f"%{term}%"
            ),
            School.address.ilike(
                f"%{term}%"
            ),
        )
        for term in search_terms
    ]

    matches = (
        School.query
        .filter(
            School.is_active.is_(True),
            and_(*term_filters),
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
