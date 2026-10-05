from dataclasses import dataclass


class BookingError(Exception):
    """Кастомний виняток для помилок бронювання."""
    pass


@dataclass
class Room:
    room_number: str
    price: float
    is_available: bool = True
    room_type: str = "Standard"

    def __post_init__(self):
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if not self.room_number.strip():
            raise ValueError("Room number cannot be empty")


@dataclass
class StandardRoom(Room):
    room_type: str = "Standard"


@dataclass
class Suite(Room):
    room_type: str = "Suite"
    has_minibar: bool = True


@dataclass
class Booking:
    booking_id: int
    room: Room
    guest_name: str
    nights: int
    status: str = "pending"

    def __post_init__(self):
        if self.nights <= 0:
            raise ValueError("Nights must be positive")

    def total_price(self) -> float:
        multiplier = 1.05 if isinstance(self.room, Suite) else 1.0
        return self.room.price * self.nights * multiplier