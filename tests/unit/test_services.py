import pytest
from unittest.mock import Mock, AsyncMock, create_autospec
from src.hotel.models import StandardRoom
from src.hotel.services import BookingService, BookingRepository, PaymentGateway, Notifier, BookingError, \
    AsyncBookingGateway


def test_repository_get_methods(standard_room):
    repo = BookingRepository()
    repo.rooms["101"] = standard_room
    assert repo.get_room("101") == standard_room
    assert repo.get_room("999") is None
    assert repo.get_booking(999) is None


def test_repository_get_available_rooms(standard_room, suite_room):
    repo = BookingRepository()
    repo.rooms["101"] = standard_room
    repo.rooms["201"] = suite_room
    suite_room.is_available = False
    available = repo.get_available_rooms()
    assert len(available) == 1
    assert available[0].room_number == "101"


def test_booking_success(valid_booking):
    repo = BookingRepository()
    # Завдання підвищеної складності: autospec замість звичайного Mock
    payment = create_autospec(PaymentGateway, instance=True)
    payment.charge.return_value = True
    notifier = create_autospec(Notifier, instance=True)

    service = BookingService(repo, payment, notifier)
    result = service.create_booking(valid_booking)

    assert result is True
    assert valid_booking.status == "confirmed"
    assert not valid_booking.room.is_available
    payment.charge.assert_called_once_with(3000.0)


def test_create_booking_unavailable_room(valid_booking):
    repo = BookingRepository()
    valid_booking.room.is_available = False
    service = BookingService(repo, Mock(), Mock())
    with pytest.raises(BookingError, match="Room is not available"):
        service.create_booking(valid_booking)


def test_payment_failure_path(valid_booking):
    repo = BookingRepository()
    payment = create_autospec(PaymentGateway, instance=True)
    payment.charge.return_value = False
    notifier = create_autospec(Notifier, instance=True)

    service = BookingService(repo, payment, notifier)
    with pytest.raises(BookingError, match="Payment failed"):
        service.create_booking(valid_booking)


def test_duplicate_booking(valid_booking):
    repo = BookingRepository()
    repo.save_booking(valid_booking)
    payment = create_autospec(PaymentGateway, instance=True)
    payment.charge.return_value = True

    service = BookingService(repo, payment, Mock())
    with pytest.raises(BookingError, match="Duplicate booking"):
        service.create_booking(valid_booking)


def test_booking_with_mocked_repo(valid_booking):
    repo = create_autospec(BookingRepository, instance=True)
    payment = create_autospec(PaymentGateway, instance=True)
    payment.charge.return_value = True

    service = BookingService(repo, payment, Mock())
    service.create_booking(valid_booking)
    repo.save_booking.assert_called_once_with(valid_booking)


def test_cancel_booking_success(valid_booking):
    repo = BookingRepository()
    valid_booking.room.is_available = False
    valid_booking.status = "confirmed"
    repo.save_booking(valid_booking)

    notifier = create_autospec(Notifier, instance=True)
    service = BookingService(repo, Mock(), notifier)

    service.cancel_booking(1)
    assert valid_booking.status == "cancelled"
    assert valid_booking.room.is_available is True
    notifier.send.assert_called_once_with("Ivan", "Booking 1 cancelled.")


def test_cancel_nonexistent_booking():
    service = BookingService(BookingRepository(), Mock(), Mock())
    with pytest.raises(BookingError, match="Booking not found"):
        service.cancel_booking(999)


def test_cancel_already_cancelled_booking(valid_booking):
    repo = BookingRepository()
    valid_booking.status = "cancelled"
    repo.save_booking(valid_booking)
    service = BookingService(repo, Mock(), Mock())
    with pytest.raises(BookingError, match="Booking already cancelled"):
        service.cancel_booking(1)


def test_repository_get_cheapest_room(standard_room, suite_room):
    repo = BookingRepository()
    assert repo.get_cheapest_room() is None  # Empty case

    repo.rooms["101"] = standard_room  # 1000.0
    repo.rooms["201"] = suite_room  # 3000.0
    assert repo.get_cheapest_room() == standard_room


def test_calculate_potential_revenue(valid_booking):
    repo = BookingRepository()
    valid_booking.status = "confirmed"
    repo.save_booking(valid_booking)

    service = BookingService(repo, Mock(), Mock())
    # 1000.0 * 3 nights = 3000.0
    assert service.calculate_potential_revenue() == 3000.0


# ЗАВДАННЯ ПІДВИЩЕНОЇ СКЛАДНОСТІ: Fake Repository
class FakeBookingRepository(BookingRepository):
    """Fake об'єкт, який імітує БД для тестів без використання Mocks."""

    def __init__(self):
        super().__init__()
        self.save_calls = 0

    def save_booking(self, booking):
        super().save_booking(booking)
        self.save_calls += 1


def test_booking_with_fake_repository(valid_booking):
    fake_repo = FakeBookingRepository()
    payment = create_autospec(PaymentGateway, instance=True)
    payment.charge.return_value = True

    service = BookingService(fake_repo, payment, Mock())
    service.create_booking(valid_booking)

    assert fake_repo.save_calls == 1
    assert 1 in fake_repo.bookings


# Завдання підвищеної складності: Test exception chaining
@pytest.mark.asyncio
async def test_async_gateway_exception_chaining():
    client = AsyncMock()
    # Піднімаємо оригінальну системну помилку
    client.get_status.side_effect = ValueError("Bad JSON")
    gateway = AsyncBookingGateway(client)

    with pytest.raises(BookingError) as exc_info:
        await gateway.fetch_external_status(999)

    # Перевіряємо, що базова причина (__cause__) збереглася
    assert isinstance(exc_info.value.__cause__, ValueError)
