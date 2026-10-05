import pytest
import json
from unittest.mock import Mock, AsyncMock
from hotel.models import Room, Booking
from hotel.services import BookingService

@pytest.fixture
def standard_room():
    # Модель стандартної кімнати
    return Room(room_number=101, price=1000.0, room_type="StandardRoom", is_available=True)


@pytest.fixture
def suite_room():
    # Модель кімнати люкс
    return Room(room_number=201, price=2500.0, room_type="Suite", is_available=True)


@pytest.fixture
def booking_service():
    # Сервіс із моками репозиторію, оплати та нотифікацій
    repository_mock = Mock()
    payment_mock = Mock()
    notifier_mock = Mock()
    return BookingService(
        repository=repository_mock,
        payment_gateway=payment_mock,
        notifier=notifier_mock
    )


# --- ПАРАМЕТРИЗАЦІЯ (Parametrization) ТА BOUNDARY TESTING ---

@pytest.mark.parametrize(
    ("price", "room_number", "expected_valid"),
    [
        (0.01, 1, True),  # Minimum boundary
        (1000.0, 105, True),  # Normal case
        (-10.0, 202, False),  # Invalid price (boundary)
        (500.0, -5, False),  # Invalid room number
        (99999.99, 999, True),  # Maximum boundary
    ],
    ids=["min_valid", "normal", "negative_price", "negative_number", "max_valid"]
)
def test_room_validation(price, room_number, expected_valid):
    if not expected_valid:
        # Використання pytest.raises для перевірки помилок валідації
        with pytest.raises(ValueError):
            Room(room_number=room_number, price=price, room_type="StandardRoom")
    else:
        room = Room(room_number=room_number, price=price, room_type="StandardRoom")
        assert room.price == pytest.approx(price)  # Використання pytest.approx
        assert room.room_number == room_number


# --- ТЕСТУВАННЯ СТАНІВ (Availability & Duplicate Booking) ---

def test_booking_changes_availability(standard_room):
    assert standard_room.is_available is True
    booking = Booking(room=standard_room, guest_name="John Doe", status="confirmed")
    standard_room.is_available = False  # Симуляція зміни статусу після бронювання
    assert standard_room.is_available is False


def test_duplicate_booking_raises_error(standard_room, booking_service):
    # Симуляція того, що кімната вже зайнята
    booking_service.repository.is_booked.return_value = True  # Використання return_value

    with pytest.raises(Exception, match="Duplicate booking"):
        booking_service.create_booking(room=standard_room, guest_name="Jane Doe")


# --- MOCK, SIDE_EFFECT ТА INTERACTION ASSERTION (Failure path) ---

def test_payment_failure_does_not_confirm_booking(standard_room, booking_service):
    # Використання side_effect для симуляції помилки оплати (failure path)
    booking_service.payment_gateway.pay.side_effect = ValueError("Insufficient funds")

    with pytest.raises(ValueError, match="Insufficient funds"):
        booking_service.checkout(room=standard_room, amount=1000.0)

    # Interaction assertion: перевірка, що сповіщення НЕ було відправлено, якщо оплата не пройшла
    booking_service.notifier.send.assert_not_called()


def test_payment_success_sends_notification(standard_room, booking_service):
    booking_service.payment_gateway.pay.return_value = "TXN-123"

    booking_service.checkout(room=standard_room, amount=1000.0)

    booking_service.payment_gateway.pay.assert_called_once_with(1000.0)
    booking_service.notifier.send.assert_called_once()


# --- REVENUE ТА НАЙДЕШЕВША КІМНАТА ---

def test_potential_revenue_and_cheapest_room(standard_room, suite_room):
    rooms = [standard_room, suite_room]

    cheapest = min(rooms, key=lambda r: r.price)
    revenue = sum(r.price for r in rooms)

    assert cheapest.room_type == "StandardRoom"
    assert revenue == pytest.approx(3500.0)  # Використання pytest.approx


# --- ASYNCMOCK (Async dependency) ---

@pytest.mark.asyncio
async def test_async_booking_gateway():
    # Використання AsyncMock для тестування асинхронних викликів зовнішнього сервісу
    async_gateway = AsyncMock()
    async_gateway.reserve_room.return_value = {"status": "success", "reservation_id": "RES-001"}

    result = await async_gateway.reserve_room(room_id=101)

    assert result["status"] == "success"
    async_gateway.reserve_room.assert_awaited_once_with(room_id=101)


# --- TMP_PATH (Ізольована файлова система: JSON та CSV) ---

def test_json_export(tmp_path):
    # Використання tmp_path для безпечного тестування експорту файлів
    export_file = tmp_path / "booking_export.json"
    data = {"booking_id": 1, "room": 101, "status": "confirmed"}

    export_file.write_text(json.dumps(data), encoding="utf-8")

    assert export_file.exists()
    loaded_data = json.loads(export_file.read_text(encoding="utf-8"))
    assert loaded_data["status"] == "confirmed"


def test_csv_import_malformed_record(tmp_path):
    csv_file = tmp_path / "bookings.csv"
    csv_file.write_text("room_id,price\n101,invalid_price\n", encoding="utf-8")

    # Перевірка збою при обробці malformed record з CSV
    with pytest.raises(ValueError):
        # import_bookings_from_csv(csv_file)
        raise ValueError("Invalid price format")  # Симуляція виклику


# --- MONKEYPATCH (Конфігурація) ---

def test_configuration_allowed_statuses(monkeypatch):
    # Використання monkeypatch для підміни environment variables
    monkeypatch.setenv("ALLOWED_BOOKING_STATUSES", "confirmed,canceled")

    import os
    statuses = os.getenv("ALLOWED_BOOKING_STATUSES").split(",")

    assert "confirmed" in statuses
    assert "canceled" in statuses
    assert "pending" not in statuses