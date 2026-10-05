from typing import Protocol, Optional
from src.hotel.models import Room, Booking, BookingError


class PaymentGateway(Protocol):
    def charge(self, amount: float) -> bool: ...


class Notifier(Protocol):
    def send(self, guest_name: str, message: str) -> None: ...


class BookingRepository:
    def __init__(self):
        self.bookings: dict[int, Booking] = {}
        self.rooms: dict[str, Room] = {}

    def save_booking(self, booking: Booking) -> None:
        if booking.booking_id in self.bookings:
            raise BookingError("Duplicate booking")
        self.bookings[booking.booking_id] = booking

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        return self.bookings.get(booking_id)

    def get_room(self, room_number: str) -> Optional[Room]:
        return self.rooms.get(room_number)

    def get_available_rooms(self) -> list[Room]:
        return [room for room in self.rooms.values() if room.is_available]


class BookingService:
    def __init__(self, repo: BookingRepository, payment: PaymentGateway, notifier: Notifier):
        self.repo = repo
        self.payment = payment
        self.notifier = notifier

    def create_booking(self, booking: Booking) -> bool:
        if not booking.room.is_available:
            raise BookingError("Room is not available")

        success = self.payment.charge(booking.total_price())
        if not success:
            raise BookingError("Payment failed")

        booking.status = "confirmed"
        booking.room.is_available = False
        self.repo.save_booking(booking)
        self.notifier.send(booking.guest_name, f"Booking {booking.booking_id} confirmed!")
        return True

    def cancel_booking(self, booking_id: int) -> bool:
        booking = self.repo.get_booking(booking_id)
        if not booking:
            raise BookingError("Booking not found")
        if booking.status == "cancelled":
            raise BookingError("Booking already cancelled")

        booking.status = "cancelled"
        booking.room.is_available = True
        self.notifier.send(booking.guest_name, f"Booking {booking_id} cancelled.")
        return True


class AsyncBookingGateway:
    def __init__(self, client):
        self._client = client

    async def fetch_external_status(self, booking_id: int) -> str:
        response = await self._client.get_status(booking_id)
        return response.get("status", "unknown")