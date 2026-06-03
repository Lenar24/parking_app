"""Тесты API клиентов"""

import json

import pytest

from app.models import Client


class TestClientsAPI:

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/clients",
            "/api/clients/1",
        ],
    )
    def test_get_methods_return_200(self, client, test_client, endpoint):
        """Параметризованный тест: все GET-методы возвращают 200"""
        if endpoint.endswith("/1"):
            endpoint = f"/api/clients/{test_client.id}"

        response = client.get(endpoint)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_get_clients_list(self, client, multiple_clients):
        """Тест получения списка всех клиентов"""
        response = client.get("/api/clients")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["count"] == len(multiple_clients)

    def test_get_client_by_id(self, client, test_client):
        """Тест получения клиента по ID"""
        response = client.get(f"/api/clients/{test_client.id}")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["id"] == test_client.id
        assert data["data"]["name"] == test_client.name

    def test_get_client_not_found(self, client):
        """Тест получения несуществующего клиента"""
        response = client.get("/api/clients/99999")
        assert response.status_code == 404

    def test_create_client_success(self, client, db):
        """Тест успешного создания клиента"""
        initial_count = len(Client.query.all())

        new_client = {
            "name": "Новый",
            "surname": "Клиент",
            "credit_card": "9999-8888-7777-6666",
            "car_number": "NEW789",
        }

        response = client.post(
            "/api/clients", data=json.dumps(new_client), content_type="application/json"
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True

        # Проверяем увеличение количества записей
        assert len(Client.query.all()) == initial_count + 1
        assert data["data"]["id"] is not None

    def test_create_client_without_name(self, client):
        """Тест создания клиента без обязательного поля name"""
        new_client = {"surname": "Клиент"}

        response = client.post(
            "/api/clients", data=json.dumps(new_client), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
