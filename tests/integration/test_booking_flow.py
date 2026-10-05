import pytest
from unittest.mock import Mock
from src.hotel.models import StandardRoom, Booking
from src.hotel.services import BookingRepository, BookingService


@pytest.mark.integration
def test_full_booking_pipeline_with_cancellation():
    """Інтеграційний тест: перевірка всього ланцюжка бронювання та його скасування."""
    room = StandardRoom("101", 1000.0)
    booking = Booking(1, room, "TestGuest", 2)

    repo = BookingRepository()
    repo.rooms[room.room_number] = room
    payment_gateway = Mock()
    payment_gateway.charge.return_value = True
    notifier = Mock()

    service = BookingService(repo, payment_gateway, notifier)

    # 1. Бронюємо
    service.create_booking(booking)
    assert repo.bookings[1].status == "confirmed"
    assert len(repo.get_available_rooms()) == 0

    # Розрахунок потенційного доходу (revenue)
    total_revenue = sum(b.total_price() for b in repo.bookings.values())
    assert total_revenue == 2000.0

    # 2. Скасовуємо
    service.cancel_booking(1)
    assert repo.bookings[1].status == "cancelled"
    assert len(repo.get_available_rooms()) == 1  # Кімната знову вільна