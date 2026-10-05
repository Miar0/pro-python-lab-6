import pytest
from unittest.mock import Mock, AsyncMock
from src.hotel.services import BookingService, BookingRepository, PaymentGateway, Notifier, BookingError, \
    AsyncBookingGateway


def test_booking_success(valid_booking):
    repo = BookingRepository()
    payment = Mock(spec=PaymentGateway)
    payment.charge.return_value = True  # return_value
    notifier = Mock(spec=Notifier)

    service = BookingService(repo, payment, notifier)
    result = service.create_booking(valid_booking)

    assert result is True
    assert valid_booking.status == "confirmed"
    assert not valid_booking.room.is_available

    # Interaction assertions
    payment.charge.assert_called_once_with(3000.0)
    notifier.send.assert_called_once_with("Ivan", "Booking 1 confirmed!")


def test_payment_failure_path(valid_booking):
    repo = BookingRepository()
    payment = Mock(spec=PaymentGateway)
    payment.charge.return_value = False  # Failure path
    notifier = Mock(spec=Notifier)

    service = BookingService(repo, payment, notifier)

    with pytest.raises(BookingError, match="Payment failed"):
        service.create_booking(valid_booking)

    notifier.send.assert_not_called()


def test_duplicate_booking(valid_booking):
    repo = BookingRepository()
    repo.save_booking(valid_booking)  # Зберігаємо перший раз

    # side_effect не потрібен явно, бо репозиторій кине помилку сам, але мокнемо платіж
    payment = Mock(spec=PaymentGateway)
    payment.charge.return_value = True
    notifier = Mock(spec=Notifier)

    service = BookingService(repo, payment, notifier)
    with pytest.raises(BookingError, match="Duplicate booking"):
        service.create_booking(valid_booking)


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