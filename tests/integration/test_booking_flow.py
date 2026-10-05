import pytest
from unittest.mock import Mock
from src.hotel.models import StandardRoom, Booking
from src.hotel.services import BookingRepository, BookingService


@pytest.mark.integration
def test_full_booking_pipeline():
    """Інтеграційний тест: перевірка всього ланцюжка без мокування репозиторію."""
    room = StandardRoom("101", 1000.0)
    booking = Booking(1, room, "TestGuest", 2)

    repo = BookingRepository()
    payment_gateway = Mock()
    payment_gateway.charge.return_value = True
    notifier = Mock()

    service = BookingService(repo, payment_gateway, notifier)

    # Діємо
    service.create_booking(booking)

    # Перевіряємо інтеграцію
    assert 1 in repo.bookings
    assert repo.bookings[1].status == "confirmed"
    assert not room.is_available
    # Розрахунок потенційного доходу (revenue)
    total_revenue = sum(b.total_price() for b in repo.bookings.values())
    assert total_revenue == 2000.0