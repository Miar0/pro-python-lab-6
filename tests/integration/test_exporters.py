import json
from src.hotel.exporters import export_bookings_to_json, import_bookings_from_csv


def test_json_export(tmp_path, bookings_list):
    output_file = tmp_path / "bookings.json"
    data = [{"id": b.booking_id, "guest": b.guest_name} for b in bookings_list]

    export_bookings_to_json(data, output_file)

    assert output_file.exists()
    saved_data = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(saved_data) == 2
    assert saved_data[0]["guest"] == "Anna"


def test_csv_import_bookings(tmp_path):
    csv_file = tmp_path / "bookings.csv"
    csv_file.write_text("id,room,status\n1,101,confirmed\n2,201,pending", encoding="utf-8")

    bookings = import_bookings_from_csv(csv_file)

    assert len(bookings) == 2
    assert bookings[0]["booking_id"] == 1
    assert bookings[1]["status"] == "pending"