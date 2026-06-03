"""Тесты API парковок"""

import json

import pytest

from app.models import Parking


class TestParkingsAPI:

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/parkings",
            "/api/parkings/1",
        ],
    )
    def test_get_methods_return_200(self, client, test_parking, endpoint):
        """Параметризованный тест: все GET-методы возвращают 200"""
        if endpoint.endswith("/1"):
            endpoint = f"/api/parkings/{test_parking.id}"

        response = client.get(endpoint)
        assert response.status_code == 200

    def test_get_parkings_list(self, client, multiple_parkings):
        """Тест получения списка всех парковок"""
        response = client.get("/api/parkings")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["count"] == len(multiple_parkings)

    def test_get_parking_by_id(self, client, test_parking):
        """Тест получения парковки по ID"""
        response = client.get(f"/api/parkings/{test_parking.id}")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["data"]["id"] == test_parking.id

    def test_get_parking_not_found(self, client):
        """Тест получения несуществующей парковки"""
        response = client.get("/api/parkings/99999")
        assert response.status_code == 404

    def test_create_parking_success(self, client, db):
        """Тест успешного создания парковки"""
        initial_count = Parking.query.count()

        new_parking = {
            "address": "Новая парковка, 1",
            "opened": True,
            "count_places": 100,
        }

        response = client.post(
            "/api/parkings",
            data=json.dumps(new_parking),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True

        # Проверяем увеличение количества записей
        assert Parking.query.count() == initial_count + 1
        assert data["data"]["id"] is not None

    def test_create_parking_without_address(self, client):
        """Тест создания парковки без адреса"""
        new_parking = {"opened": True, "count_places": 50}

        response = client.post(
            "/api/parkings",
            data=json.dumps(new_parking),
            content_type="application/json",
        )

        assert response.status_code == 400
