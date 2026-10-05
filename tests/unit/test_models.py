import pytest
from src.hotel.models import StandardRoom, Suite, Booking, Room

@pytest.mark.parametrize(
    "price",
    [
        pytest.param(0, id="zero_price"),
        pytest.param(-100, id="negative_price"),
        pytest.param(-0.01, id="small_negative_price"),
    ]
)
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

def test_invalid_booking_status(standard_room):
    with pytest.raises(ValueError, match="Invalid status") as exc_info:
        Booking(booking_id=1, room=standard_room, guest_name="Guest", nights=2, status="unknown")
    assert "Invalid status" in str(exc_info.value)

def test_standard_room_total_price(standard_room):
    # Використовуємо parameterized_price з conftest (1000.0 або 1500.0)
    booking = Booking(1, standard_room, "Guest", 3)
    assert booking.total_price() == standard_room.price * 3

def test_suite_total_price_with_tax(suite_room):
    booking = Booking(1, suite_room, "Guest", 2)
    assert booking.total_price() == pytest.approx(6300.0)