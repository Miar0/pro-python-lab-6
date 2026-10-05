import pytest
from unittest.mock import Mock, AsyncMock
from src.hotel.models import StandardRoom
from src.hotel.services import BookingRepository, BookingService, AsyncBookingGateway


@pytest.mark.integration
def test_full_booking_pipeline_with_cancellation(booking_factory):
    room = StandardRoom("101", 1000.0)
    # Використання fixture factory
    booking = booking_factory(booking_id=1, room=room, guest_name="TestGuest", nights=2)

    repo = BookingRepository()
    repo.rooms[room.room_number] = room
    payment_gateway = Mock()
    payment_gateway.charge.return_value = True
    notifier = Mock()

    service = BookingService(repo, payment_gateway, notifier)

    service.create_booking(booking)
    assert repo.bookings[1].status == "confirmed"
    assert len(repo.get_available_rooms()) == 0

    total_revenue = sum(b.total_price() for b in repo.bookings.values())
    assert total_revenue == 2000.0

    service.cancel_booking(1)
    assert repo.bookings[1].status == "cancelled"
    assert len(repo.get_available_rooms()) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_integration_reservation_flow(booking_factory):
    """Інтеграційний тест для async booking gateway."""
    room = StandardRoom("202", 1500.0)
    booking = booking_factory(2, room, "AsyncGuest")

    repo = BookingRepository()
    repo.save_booking(booking)

    # Імітуємо зовнішній сервіс
    external_client = AsyncMock()
    external_client.get_status.return_value = {"status": "paid"}
    gateway = AsyncBookingGateway(external_client)

    status = await gateway.fetch_external_status(2)

    # Інтегруємо зовнішній статус із локальною базою
    if status == "paid":
        db_booking = repo.get_booking(2)
        db_booking.status = "confirmed"

    assert repo.get_booking(2).status == "confirmed"