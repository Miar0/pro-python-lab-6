import pytest
from src.hotel.models import StandardRoom, Suite, Booking

@pytest.fixture
def standard_room():
    return StandardRoom(room_number="101", price=1000.0)

@pytest.fixture
def suite_room():
    return Suite(room_number="201", price=3000.0)

@pytest.fixture
def valid_booking(standard_room):
    return Booking(booking_id=1, room=standard_room, guest_name="Ivan", nights=3)

@pytest.fixture
def bookings_list(standard_room, suite_room):
    return [
        Booking(1, standard_room, "Anna", 2),
        Booking(2, suite_room, "Oleg", 1)
    ]