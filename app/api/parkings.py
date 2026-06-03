""" API для парковок"""

from flask import Blueprint, jsonify, request

from app.models import Parking, db

parkings_bp = Blueprint("parkings", __name__)


@parkings_bp.route("/parkings", methods=["GET"])
def get_parkings():
    """GET /api/parkings — список всех парковок"""
    parkings = db.session.execute(db.select(Parking)).scalars().all()
    return (
        jsonify(
            {
                "success": True,
                "count": len(parkings),
                "data": [parking.to_dict() for parking in parkings],
            }
        ),
        200,
    )


@parkings_bp.route("/parkings/<int:parking_id>", methods=["GET"])
def get_parking(parking_id):
    """GET /api/parkings/<int:parking_id> — информация о парковке по ID"""
    parking = db.session.get(Parking, parking_id)
    if not parking:
        return (
            jsonify(
                {"success": False, "error": f"Parking with id {parking_id} not found"}
            ),
            404,
        )

    return jsonify({"success": True, "data": parking.to_dict()}), 200


@parkings_bp.route("/parkings", methods=["POST"])
def create_parking():
    """POST /api/parkings — создать новую парковочную зону"""
    data = request.get_json()

    if not data.get("address") or not data.get("count_places"):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Address and count_places are required fields",
                }
            ),
            400,
        )

    if data["count_places"] <= 0:
        return (
            jsonify({"success": False, "error": "count_places must be greater than 0"}),
            400,
        )

    parking = Parking(
        address=data["address"],
        opened=data.get("opened", True),
        count_places=data["count_places"],
        count_available_places=data["count_places"] if data.get("opened", True) else 0,
    )

    db.session.add(parking)
    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "message": "Parking created successfully",
                "data": parking.to_dict(),
            }
        ),
        201,
    )
