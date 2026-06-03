"""API для операций парковки"""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from app.models import Client, ClientParking, Parking, db

client_parkings_bp = Blueprint("client_parkings", __name__)

PARKING_RATE_PER_MINUTE = 2.0


@client_parkings_bp.route("/client_parkings", methods=["GET"])
def get_client_parkings():
    """GET /api/client_parkings — список всех парковочных сессий"""
    client_parkings = db.session.execute(db.select(ClientParking)).scalars().all()
    return (
        jsonify(
            {
                "success": True,
                "count": len(client_parkings),
                "data": [cp.to_dict() for cp in client_parkings],
            }
        ),
        200,
    )


@client_parkings_bp.route("/client_parkings/active", methods=["GET"])
def get_active_sessions():
    """GET /api/client_parkings/active — список активных сессий"""
    active_sessions = ClientParking.query.filter_by(time_out=None).all()
    return (
        jsonify(
            {
                "success": True,
                "count": len(active_sessions),
                "data": [cp.to_dict() for cp in active_sessions],
            }
        ),
        200,
    )


@client_parkings_bp.route("/client_parkings", methods=["POST"])
def check_in():
    """POST /api/client_parkings — заезд на парковку"""
    data = request.get_json()

    if not data.get("client_id") or not data.get("parking_id"):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "client_id and parking_id are required fields",
                }
            ),
            400,
        )

    client_id = data["client_id"]
    parking_id = data["parking_id"]

    # Проверка существования клиента
    client = db.session.get(Client, client_id)
    if not client:
        return (
            jsonify(
                {"success": False, "error": f"Client with id {client_id} not found"}
            ),
            404,
        )

    # Проверка наличия привязанной карты
    if not client.credit_card:
        return (
            jsonify({"success": False, "error": "Client has no credit card attached"}),
            400,
        )

    # Проверка существования парковки
    parking = db.session.get(Parking, parking_id)
    if not parking:
        return (
            jsonify(
                {"success": False, "error": f"Parking with id {parking_id} not found"}
            ),
            404,
        )

    # Проверка, открыта ли парковка
    if not parking.opened:
        return (
            jsonify(
                {"success": False, "error": f"Parking {parking_id} is currently closed"}
            ),
            400,
        )

    # Проверка, нет ли активной парковки у клиента
    active_session = ClientParking.query.filter_by(
        client_id=client_id, time_out=None
    ).first()
    if active_session:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Client already has an active parking session",
                }
            ),
            400,
        )

    # Проверка наличия свободных мест
    if parking.count_available_places <= 0:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"No available spaces at parking {parking_id}",
                }
            ),
            400,
        )

    # Создание парковочной сессии
    client_parking = ClientParking(
        client_id=client_id,
        parking_id=parking_id,
        time_in=datetime.now(timezone.utc).replace(tzinfo=None),
    )

    # Уменьшаем количество свободных мест
    parking.count_available_places -= 1

    db.session.add(client_parking)
    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "message": "Check-in successful",
                "data": client_parking.to_dict(),
            }
        ),
        201,
    )


@client_parkings_bp.route("/client_parkings", methods=["DELETE"])
def check_out():
    """DELETE /api/client_parkings — выезд с парковки"""
    data = request.get_json()

    if not data.get("client_id") or not data.get("parking_id"):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "client_id and parking_id are required fields",
                }
            ),
            400,
        )

    client_id = data["client_id"]
    parking_id = data["parking_id"]

    # Проверка существования клиента
    client = db.session.get(Client, client_id)
    if not client:
        return (
            jsonify(
                {"success": False, "error": f"Client with id {client_id} not found"}
            ),
            404,
        )

    # Поиск активной парковочной сессии
    client_parking = ClientParking.query.filter_by(
        client_id=client_id, parking_id=parking_id, time_out=None
    ).first()

    if not client_parking:
        return (
            jsonify({"success": False, "error": "No active parking session found"}),
            404,
        )

    # Проверка наличия карты для оплаты
    if not client.credit_card:
        return (
            jsonify({"success": False, "error": "Client has no credit card attached"}),
            400,
        )

    # Расчет времени и стоимости
    time_in = client_parking.time_in
    time_out = datetime.now(timezone.utc).replace(tzinfo=None)
    duration_minutes = (time_out - time_in).total_seconds() / 60
    cost = round(duration_minutes * PARKING_RATE_PER_MINUTE, 2)

    # Обновление сессии
    client_parking.time_out = time_out

    # Увеличиваем количество свободных мест
    parking = db.session.get(Parking, parking_id)
    if parking:
        parking.count_available_places += 1

    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "message": "Check-out successful. Payment processed.",
                "data": {
                    "session": client_parking.to_dict(),
                    "payment": {
                        "client_id": client_id,
                        "duration_minutes": round(duration_minutes, 2),
                        "cost": cost,
                        "currency": "RUB",
                    },
                },
            }
        ),
        200,
    )


@client_parkings_bp.route("/client_parkings/client/<int:client_id>", methods=["GET"])
def get_client_parking_history(client_id):
    """GET /api/client_parkings/client/<int:client_id> — история парковок клиента"""
    client = Client.query.get(client_id)
    if not client:
        return (
            jsonify(
                {"success": False, "error": f"Client with id {client_id} not found"}
            ),
            404,
        )

    parking_history = ClientParking.query.filter_by(client_id=client_id).all()

    return (
        jsonify(
            {
                "success": True,
                "client": client.to_dict(),
                "count": len(parking_history),
                "history": [cp.to_dict() for cp in parking_history],
            }
        ),
        200,
    )


@client_parkings_bp.route("/client_parkings/parking/<int:parking_id>", methods=["GET"])
def get_parking_sessions(parking_id):
    """GET /api/client_parkings/parking/<int:parking_id> — все сессии парковки"""
    parking = Parking.query.get(parking_id)
    if not parking:
        return (
            jsonify(
                {"success": False, "error": f"Parking with id {parking_id} not found"}
            ),
            404,
        )

    sessions = ClientParking.query.filter_by(parking_id=parking_id).all()

    return (
        jsonify(
            {
                "success": True,
                "parking": parking.to_dict(),
                "count": len(sessions),
                "sessions": [session.to_dict() for session in sessions],
            }
        ),
        200,
    )
