import pytest
from src.hotel.models import StandardRoom, Suite, Booking

@pytest.fixture(scope="session", autouse=True)
def global_test_setup():
    """Autouse фікстура з yield (Завдання підвищеної складності)."""
    # Setup
    yield
    # Teardown
    pass

@pytest.fixture(params=[1000.0, 1500.0])
def parameterized_price(request):
    """Parameterized fixture (Завдання підвищеної складності)."""
    return request.param

@pytest.fixture
def standard_room(parameterized_price):
    return StandardRoom(room_number="101", price=parameterized_price)

@pytest.fixture
def suite_room():
    return Suite(room_number="201", price=3000.0)

@pytest.fixture
def valid_booking(standard_room):
    return Booking(booking_id=1, room=standard_room, guest_name="Ivan", nights=3)

@pytest.fixture
def booking_factory():
    """Fixture factory."""
    def create_booking(booking_id: int, room, guest_name: str = "Guest", nights: int = 1):
        return Booking(booking_id=booking_id, room=room, guest_name=guest_name, nights=nights)
    return create_booking