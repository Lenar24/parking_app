class TestParkingModels:
    """Тесты моделей парковки"""

    def test_parking_has_available_spaces(self, test_parking):
        """Тест метода has_available_spaces"""
        assert test_parking.has_available_spaces() is True

        test_parking.count_available_places = 0
        assert test_parking.has_available_spaces() is False

    def test_parking_occupy_space(self, test_parking):
        """Тест метода occupy_space"""
        initial = test_parking.count_available_places

        result = test_parking.occupy_space()

        assert result is True
        assert test_parking.count_available_places == initial - 1

    def test_parking_free_space(self, test_parking):
        """Тест метода free_space"""
        test_parking.count_available_places = 0

        result = test_parking.free_space()

        assert result is True
        assert test_parking.count_available_places == 1
