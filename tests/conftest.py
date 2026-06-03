"""Фикстуры для тестов"""

import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import text

from app import create_app
from app.models import Client, ClientParking, Parking
from app.models import db as _db


@pytest.fixture(scope="session")
def app():
    """Фикстура приложения для тестирования"""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app("testing")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def client(app):
    """Фикстура тестового клиента для HTTP-запросов"""
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    """Фикстура для работы с базой данных"""
    with app.app_context():
        # Очищаем все таблицы перед тестом (используем text())
        _db.session.execute(text("DELETE FROM client_parking"))
        _db.session.execute(text("DELETE FROM client"))
        _db.session.execute(text("DELETE FROM parking"))
        _db.session.commit()

        yield _db

        # Откатываем изменения после теста
        _db.session.rollback()


@pytest.fixture(scope="function")
def test_client(db):
    """Фикстура тестового клиента из БД"""
    client = Client(
        name="Иван",
        surname="Тестовый",
        credit_card="1234-5678-9012-3456",
        car_number="TEST123",
    )
    db.session.add(client)
    db.session.commit()
    return client


@pytest.fixture(scope="function")
def test_client_without_card(db):
    """Фикстура тестового клиента без карты"""
    client = Client(
        name="Петр", surname="Безкарточный", credit_card=None, car_number="NOCARD"
    )
    db.session.add(client)
    db.session.commit()
    return client


@pytest.fixture(scope="function")
def test_parking(db):
    """Фикстура тестовой парковки"""
    parking = Parking(
        address="ул. Тестовая, 123",
        opened=True,
        count_places=10,
        count_available_places=5,
    )
    db.session.add(parking)
    db.session.commit()
    return parking


@pytest.fixture(scope="function")
def test_closed_parking(db):
    """Фикстура закрытой парковки"""
    parking = Parking(
        address="ул. Закрытая, 456",
        opened=False,
        count_places=20,
        count_available_places=0,
    )
    db.session.add(parking)
    db.session.commit()
    return parking


@pytest.fixture(scope="function")
def test_full_parking(db):
    """Фикстура полностью заполненной парковки"""
    parking = Parking(
        address="ул. Полная, 789", opened=True, count_places=5, count_available_places=0
    )
    db.session.add(parking)
    db.session.commit()
    return parking


@pytest.fixture(scope="function")
def test_parking_log(db, test_client, test_parking):
    """Фикстура лога парковки с фиксацией времени"""
    # Используем UTC время
    time_in = datetime.now(timezone.utc) - timedelta(hours=2)
    # Убираем информацию о часовом поясе для SQLite
    time_in = time_in.replace(tzinfo=None)

    log = ClientParking(
        client_id=test_client.id,
        parking_id=test_parking.id,
        time_in=time_in,
        time_out=None,
    )
    db.session.add(log)
    test_parking.count_available_places -= 1
    db.session.commit()
    return log


@pytest.fixture(scope="function")
def multiple_parkings(db):
    """Фикстура нескольких парковок"""
    # Очищаем существующие данные
    db.session.execute(text("DELETE FROM parking"))
    db.session.commit()

    parkings = [
        Parking(
            address="ул. Парковая, 1",
            opened=True,
            count_places=50,
            count_available_places=30,
        ),
        Parking(
            address="ул. Парковая, 2",
            opened=True,
            count_places=30,
            count_available_places=15,
        ),
        Parking(
            address="ул. Парковая, 3",
            opened=False,
            count_places=20,
            count_available_places=0,
        ),
    ]
    for parking in parkings:
        db.session.add(parking)
    db.session.commit()
    return parkings


@pytest.fixture(scope="function")
def multiple_clients(db):
    """Фикстура нескольких клиентов"""
    # Очищаем существующие данные
    db.session.execute(text("DELETE FROM client"))
    db.session.commit()

    clients = [
        Client(
            name="Анна",
            surname="Петрова",
            credit_card="1111-2222-3333-4444",
            car_number="A111AA",
        ),
        Client(
            name="Сергей",
            surname="Иванов",
            credit_card="5555-6666-7777-8888",
            car_number="B222BB",
        ),
        Client(name="Елена", surname="Сидорова", credit_card=None, car_number="C333CC"),
    ]
    for client in clients:
        db.session.add(client)
    db.session.commit()
    return clients
