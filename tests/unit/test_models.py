import pytest
from src.hotel.models import StandardRoom, Suite, Booking, Room

@pytest.mark.parametrize("price", [0, -100, -0.01])
def test_invalid_room_price(price):
    with pytest.raises(ValueError, match="positive"):
        Room(room_number="101", price=price)

def test_empty_room_number():
    with pytest.raises(ValueError, match="cannot be empty"):
        Room(room_number="   ", price=1000)

@pytest.mark.parametrize("nights", [0, -5])
def test_invalid_booking_nights(standard_room, nights):
    with pytest.raises(ValueError, match="positive"):
        Booking(booking_id=1, room=standard_room, guest_name="Guest", nights=nights)

def test_standard_room_total_price(standard_room):
    booking = Booking(1, standard_room, "Guest", 3)
    assert booking.total_price() == 3000.0

def test_suite_total_price_with_tax(suite_room):
    booking = Booking(1, suite_room, "Guest", 2)
    assert booking.total_price() == pytest.approx(6300.0)

def test_cheapest_room():
    rooms = [Room("1", 500), Room("2", 300), Room("3", 1000)]
    cheapest = min(rooms, key=lambda r: r.price)
    assert cheapest.price == 300