"""Тесты операций парковки"""

import json

import pytest

from app.models import ClientParking, Parking


class TestClientParkingsAPI:

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/client_parkings",
            "/api/client_parkings/active",
        ],
    )
    def test_get_methods_return_200(self, client, endpoint):
        """Параметризованный тест: GET-методы возвращают 200"""
        response = client.get(endpoint)
        assert response.status_code == 200

    @pytest.mark.parking
    def test_check_in_success(self, client, db, test_client, test_parking):
        """Тест успешного заезда на парковку"""
        initial_available = test_parking.count_available_places

        check_in_data = {"client_id": test_client.id, "parking_id": test_parking.id}

        response = client.post(
            "/api/client_parkings",
            data=json.dumps(check_in_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True

        # Проверяем уменьшение количества свободных мест
        updated_parking = db.session.get(Parking, test_parking.id)
        assert updated_parking.count_available_places == initial_available - 1

    @pytest.mark.parking
    def test_check_in_without_credit_card(
        self, client, test_client_without_card, test_parking
    ):
        """Тест заезда клиента без привязанной карты"""
        check_in_data = {
            "client_id": test_client_without_card.id,
            "parking_id": test_parking.id,
        }

        response = client.post(
            "/api/client_parkings",
            data=json.dumps(check_in_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "credit card" in data["error"].lower()

    @pytest.mark.parking
    def test_check_in_on_closed_parking(self, client, test_client, test_closed_parking):
        """Тест заезда на закрытую парковку"""
        check_in_data = {
            "client_id": test_client.id,
            "parking_id": test_closed_parking.id,
        }

        response = client.post(
            "/api/client_parkings",
            data=json.dumps(check_in_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "closed" in data["error"].lower()

    @pytest.mark.parking
    def test_check_in_on_full_parking(self, client, test_client, test_full_parking):
        """Тест заезда на полностью заполненную парковку"""
        check_in_data = {
            "client_id": test_client.id,
            "parking_id": test_full_parking.id,
        }

        response = client.post(
            "/api/client_parkings",
            data=json.dumps(check_in_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "No available spaces" in data["error"]

    @pytest.mark.parking
    def test_check_out_success(self, client, db, test_parking_log, test_parking):
        """Тест успешного выезда с парковки"""
        initial_available = test_parking.count_available_places

        check_out_data = {
            "client_id": test_parking_log.client_id,
            "parking_id": test_parking_log.parking_id,
        }

        response = client.delete(
            "/api/client_parkings",
            data=json.dumps(check_out_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "Check-out successful" in data["message"]

        # Проверяем увеличение количества свободных мест
        updated_parking = db.session.get(Parking, test_parking.id)
        assert updated_parking.count_available_places == initial_available + 1

        # Проверяем, что время выезда проставлено
        session = db.session.get(ClientParking, test_parking_log.id)
        assert session.time_out is not None

        # Проверяем, что длительность парковки положительная (из API ответа)
        assert data["data"]["payment"]["duration_minutes"] > 0

        # Проверяем, что оплата произведена
        payment = data["data"]["payment"]
        assert payment["client_id"] == test_parking_log.client_id
        assert payment["cost"] > 0

    @pytest.mark.parking
    def test_check_out_without_active_session(self, client, test_client, test_parking):
        """Тест выезда без активной сессии"""
        check_out_data = {"client_id": test_client.id, "parking_id": test_parking.id}

        response = client.delete(
            "/api/client_parkings",
            data=json.dumps(check_out_data),
            content_type="application/json",
        )

        assert response.status_code == 404
