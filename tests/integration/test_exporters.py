import json
from src.hotel.exporters import export_bookings_to_json, import_rooms_from_csv


def test_json_export(tmp_path, bookings_list):
    output_file = tmp_path / "bookings.json"
    data = [{"id": b.booking_id, "guest": b.guest_name} for b in bookings_list]

    export_bookings_to_json(data, output_file)

    assert output_file.exists()
    saved_data = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(saved_data) == 2
    assert saved_data[0]["guest"] == "Anna"


def test_csv_import(tmp_path):
    csv_file = tmp_path / "rooms.csv"
    csv_file.write_text("number,price\n101,1000\n102,1500", encoding="utf-8")

    rooms = import_rooms_from_csv(csv_file)

    assert len(rooms) == 2
    assert rooms[0].room_number == "101"
    assert rooms[1].price == 1500.0