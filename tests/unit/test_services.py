import pytest
from unittest.mock import Mock, AsyncMock
from src.hotel.services import BookingService, BookingRepository, PaymentGateway, Notifier, BookingError, \
    AsyncBookingGateway


# --- Тестування Repository ---
def test_repository_get_available_rooms(standard_room, suite_room):
    repo = BookingRepository()
    repo.rooms["101"] = standard_room
    repo.rooms["201"] = suite_room

    suite_room.is_available = False  # Зайняли одну кімнату
    available = repo.get_available_rooms()

    assert len(available) == 1
    assert available[0].room_number == "101"


# --- Тестування Service ---
def test_booking_success(valid_booking):
    repo = BookingRepository()
    payment = Mock(spec=PaymentGateway)
    payment.charge.return_value = True
    notifier = Mock(spec=Notifier)

    service = BookingService(repo, payment, notifier)
    result = service.create_booking(valid_booking)

    assert result is True
    assert valid_booking.status == "confirmed"
    assert not valid_booking.room.is_available
    payment.charge.assert_called_once_with(3000.0)


def test_payment_failure_path(valid_booking):
    repo = BookingRepository()
    payment = Mock(spec=PaymentGateway)
    payment.charge.return_value = False
    notifier = Mock(spec=Notifier)

    service = BookingService(repo, payment, notifier)
    with pytest.raises(BookingError, match="Payment failed"):
        service.create_booking(valid_booking)


def test_duplicate_booking(valid_booking):
    repo = BookingRepository()
    repo.save_booking(valid_booking)

    payment = Mock(spec=PaymentGateway)
    payment.charge.return_value = True
    notifier = Mock()

    service = BookingService(repo, payment, notifier)
    with pytest.raises(BookingError, match="Duplicate booking"):
        service.create_booking(valid_booking)


def test_booking_with_mocked_repo(valid_booking):
    """Використання Mock для BookingRepository (вимога 8-го варіанта)."""
    repo = Mock(spec=BookingRepository)
    payment = Mock(spec=PaymentGateway)
    payment.charge.return_value = True
    notifier = Mock(spec=Notifier)

    service = BookingService(repo, payment, notifier)
    service.create_booking(valid_booking)

    repo.save_booking.assert_called_once_with(valid_booking)


def test_cancel_booking_success(valid_booking):
    repo = BookingRepository()
    valid_booking.room.is_available = False
    valid_booking.status = "confirmed"
    repo.save_booking(valid_booking)

    notifier = Mock(spec=Notifier)
    service = BookingService(repo, Mock(), notifier)

    service.cancel_booking(1)

    assert valid_booking.status == "cancelled"
    assert valid_booking.room.is_available is True
    notifier.send.assert_called_once_with("Ivan", "Booking 1 cancelled.")


def test_cancel_nonexistent_booking():
    repo = BookingRepository()
    service = BookingService(repo, Mock(), Mock())
    with pytest.raises(BookingError, match="Booking not found"):
        service.cancel_booking(999)


def test_cancel_already_cancelled_booking(valid_booking):
    repo = BookingRepository()
    valid_booking.status = "cancelled"
    repo.save_booking(valid_booking)

    service = BookingService(repo, Mock(), Mock())
    with pytest.raises(BookingError, match="Booking already cancelled"):
        service.cancel_booking(1)


def test_repository_get_methods(standard_room):
    repo = BookingRepository()
    repo.rooms["101"] = standard_room

    # Перевірка пошуку існуючої та неіснуючої кімнати
    assert repo.get_room("101") == standard_room
    assert repo.get_room("999") is None

    # Перевірка пошуку неіснуючого бронювання
    assert repo.get_booking(999) is None


def test_create_booking_unavailable_room(valid_booking):
    repo = BookingRepository()
    # Імітуємо, що кімната вже зайнята
    valid_booking.room.is_available = False
    service = BookingService(repo, Mock(), Mock())

    with pytest.raises(BookingError, match="Room is not available"):
        service.create_booking(valid_booking)


# --- Тестування Async ---
@pytest.mark.asyncio
async def test_async_gateway_success():
    client = AsyncMock()
    client.get_status.return_value = {"status": "confirmed"}

    gateway = AsyncBookingGateway(client)
    status = await gateway.fetch_external_status(999)

    assert status == "confirmed"
    client.get_status.assert_awaited_once_with(999)


@pytest.mark.asyncio
async def test_async_gateway_failure():
    client = AsyncMock()
    client.get_status.side_effect = ConnectionError("Timeout")

    gateway = AsyncBookingGateway(client)
    with pytest.raises(ConnectionError):
        await gateway.fetch_external_status(999)