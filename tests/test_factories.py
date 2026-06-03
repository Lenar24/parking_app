"""Тесты с Factory Boy"""

import json

from app.models import Client, Parking
from tests.factories import (
    ClientFactory,
    ClientWithCardFactory,
    ClientWithoutCardFactory,
    ParkingFactory,
)


class TestFactories:

    def test_client_factory_creates_client(self, db):
        """Тест создания клиента через фабрику"""
        initial_count = Client.query.count()

        client = ClientFactory()

        assert client.id is not None
        assert Client.query.count() == initial_count + 1
        assert client.name is not None
        assert client.surname is not None

    def test_parking_factory_creates_parking(self, db):
        """Тест создания парковки через фабрику"""
        initial_count = Parking.query.count()

        parking = ParkingFactory()

        assert parking.id is not None
        assert Parking.query.count() == initial_count + 1
        assert parking.address is not None

    def test_client_with_card_factory(self, db):
        """Тест фабрики клиентов с картой"""
        client = ClientWithCardFactory()
        assert client.credit_card is not None

    def test_client_without_card_factory(self, db):
        """Тест фабрики клиентов без карты"""
        client = ClientWithoutCardFactory()
        assert client.credit_card is None

    def test_create_client_using_factory_duplicate(self, client, db):
        """
        Дубликат теста «Создание клиента» из задания 3,
        переписанный с использованием ClientFactory
        """
        initial_count = Client.query.count()

        # Создаем клиента через фабрику (build - не сохраняет в БД)
        new_client = ClientFactory.build()

        response = client.post(
            "/api/clients",
            data=json.dumps(
                {
                    "name": new_client.name,
                    "surname": new_client.surname,
                    "credit_card": new_client.credit_card,
                    "car_number": new_client.car_number,
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True

        # Проверяем увеличение количества записей
        assert Client.query.count() == initial_count + 1

        # Проверяем наличие ID у новой записи
        assert data["data"]["id"] is not None
        assert isinstance(data["data"]["id"], int)

        # Проверяем, что данные сохранены корректно
        created_client = db.session.get(Client, data["data"]["id"])
        assert created_client.name == new_client.name
        assert created_client.surname == new_client.surname

    def test_create_parking_using_factory_duplicate(self, client, db):
        """
        Дубликат теста «Создание парковки» из задания 3,
        переписанный с использованием ParkingFactory
        """
        initial_count = Parking.query.count()

        # Создаем парковку через фабрику
        new_parking = ParkingFactory.build()

        response = client.post(
            "/api/parkings",
            data=json.dumps(
                {
                    "address": new_parking.address,
                    "opened": new_parking.opened,
                    "count_places": new_parking.count_places,
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True

        # Проверяем увеличение количества записей
        assert Parking.query.count() == initial_count + 1

        # Проверяем наличие ID у новой записи
        assert data["data"]["id"] is not None
        assert isinstance(data["data"]["id"], int)

        # Проверяем, что данные сохранены корректно
        created_parking = db.session.get(Parking, data["data"]["id"])
        assert created_parking.address == new_parking.address
        assert created_parking.count_places == new_parking.count_places
