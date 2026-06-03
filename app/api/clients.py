"""API для клиентов"""

from flask import Blueprint, jsonify, request

from app.models import Client, db

clients_bp = Blueprint("clients", __name__)


@clients_bp.route("/clients", methods=["GET"])
def get_clients():
    """GET /api/clients — список всех клиентов"""
    clients = db.session.execute(db.select(Client)).scalars().all()
    return (
        jsonify(
            {
                "success": True,
                "count": len(clients),
                "data": [client.to_dict() for client in clients],
            }
        ),
        200,
    )


@clients_bp.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    """GET /api/clients/<int:client_id> — информация клиента по ID"""
    client = db.session.get(Client, client_id)
    if not client:
        return (
            jsonify(
                {"success": False, "error": f"Client with id {client_id} not found"}
            ),
            404,
        )

    return jsonify({"success": True, "data": client.to_dict()}), 200


@clients_bp.route("/clients", methods=["POST"])
def create_client():
    """POST /api/clients — создать нового клиента"""
    data = request.get_json()

    if not data.get("name") or not data.get("surname"):
        return (
            jsonify(
                {"success": False, "error": "Name and surname are required fields"}
            ),
            400,
        )

    client = Client(
        name=data["name"],
        surname=data["surname"],
        credit_card=data.get("credit_card"),
        car_number=data.get("car_number"),
    )

    db.session.add(client)
    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "message": "Client created successfully",
                "data": client.to_dict(),
            }
        ),
        201,
    )
