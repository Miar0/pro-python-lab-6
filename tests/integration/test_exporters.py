import json
import pytest
from src.hotel.exporters import export_bookings_to_json, import_bookings_from_csv
from src.hotel.models import Booking


def test_json_export(tmp_path, booking_factory, standard_room):
    b1 = booking_factory(1, standard_room, "Anna")
    b2 = booking_factory(2, standard_room, "Oleg")

    output_file = tmp_path / "bookings.json"
    data = [{"id": b.booking_id, "guest": b.guest_name} for b in [b1, b2]]

    export_bookings_to_json(data, output_file)

    assert output_file.exists()
    saved_data = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(saved_data) == 2
    assert saved_data[0]["guest"] == "Anna"


def test_csv_import_bookings(tmp_path):
    csv_file = tmp_path / "bookings.csv"
    csv_file.write_text("id,room,status\n1,101,confirmed\n2,201,pending", encoding="utf-8")

    # Використовуємо list() бо тепер це генератор (yield)
    bookings = list(import_bookings_from_csv(csv_file))

    assert len(bookings) == 2
    assert bookings[0]["booking_id"] == 1
    assert bookings[1]["status"] == "pending"


def test_atomic_export_failure(tmp_path):
    output_file = tmp_path / "bookings.json"
    output_file.write_text("old valid data", encoding="utf-8")

    with pytest.raises(TypeError):
        export_bookings_to_json([{"bad_field": set()}], output_file)

    assert output_file.read_text(encoding="utf-8") == "old valid data"
    assert not output_file.with_suffix('.tmp').exists()

def test_csv_import_malformed_record(tmp_path):
    csv_file = tmp_path / "bad_bookings.csv"
    # Передаємо невалідний id (текст замість числа), що має викликати помилку при int(row["id"])
    csv_file.write_text("id,room,status\ninvalid_id,101,confirmed\n", encoding="utf-8")

    with pytest.raises(ValueError):
        list(import_bookings_from_csv(csv_file))