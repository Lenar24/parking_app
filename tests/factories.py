"""Фабрики для Factory Boy"""

import random

import factory
from factory import LazyAttribute, Sequence
from factory.fuzzy import FuzzyInteger

from app.models import Client, Parking, db


def generate_car_number():
    """Генерация российского номера автомобиля"""
    letters = "АВЕКМНОРСТУХ"
    numbers = "0123456789"
    letter1 = random.choice(letters)
    digits = "".join(random.choice(numbers) for _ in range(3))
    letter2 = random.choice(letters)
    letter3 = random.choice(letters)
    region = random.choice(["77", "177", "777", "99", "199", "799"])
    return f"{letter1}{digits}{letter2}{letter3}{region}"


def generate_credit_card():
    """Генерация номера кредитной карты"""
    # 50% вероятность, что карты нет
    if random.choice([True, False]):
        return None
    # Генерируем номер карты
    return (
        f"{random.randint(1000, 9999)}-"
        f"{random.randint(1000, 9999)}-"
        f"{random.randint(1000, 9999)}-"
        f"{random.randint(1000, 9999)}"
    )


def generate_name():
    """Генерация имени"""
    names = [
        "Иван",
        "Петр",
        "Анна",
        "Мария",
        "Сергей",
        "Елена",
        "Алексей",
        "Ольга",
        "Дмитрий",
        "Татьяна",
    ]
    return random.choice(names)


def generate_surname():
    """Генерация фамилии"""
    surnames = [
        "Иванов",
        "Петров",
        "Сидоров",
        "Смирнова",
        "Кузнецов",
        "Попова",
        "Васильев",
        "Павлова",
    ]
    return random.choice(surnames)


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика для создания клиентов"""

    class Meta:
        model = Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    name = LazyAttribute(lambda _: generate_name())
    surname = LazyAttribute(lambda _: generate_surname())
    credit_card = LazyAttribute(lambda _: generate_credit_card())
    car_number = LazyAttribute(lambda _: generate_car_number())


class ClientWithCardFactory(ClientFactory):
    """Фабрика клиента с картой"""

    credit_card = LazyAttribute(
        lambda _: f"{random.randint(1000, 9999)}-"
        f"{random.randint(1000, 9999)}-"
        f"{random.randint(1000, 9999)}-"
        f"{random.randint(1000, 9999)}"
    )


class ClientWithoutCardFactory(ClientFactory):
    """Фабрика клиента без карты"""

    credit_card = None


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика для создания парковок"""

    class Meta:
        model = Parking
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    address = Sequence(lambda n: f"ул. Тестовая, {n}")
    opened = LazyAttribute(lambda _: random.choice([True, False]))
    count_places = FuzzyInteger(10, 200)
    count_available_places = LazyAttribute(lambda o: o.count_places if o.opened else 0)


class OpenParkingFactory(ParkingFactory):
    """Фабрика открытой парковки"""

    opened = True
    count_available_places = LazyAttribute(lambda o: o.count_places)


class ClosedParkingFactory(ParkingFactory):
    """Фабрика закрытой парковки"""

    opened = False
    count_available_places = 0


class FullParkingFactory(ParkingFactory):
    """Фабрика полной парковки"""

    count_places = 50
    count_available_places = 0
    opened = True


class EmptyParkingFactory(ParkingFactory):
    """Фабрика пустой парковки"""

    count_available_places = LazyAttribute(lambda o: o.count_places)
    opened = True
