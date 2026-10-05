import json
import csv
from pathlib import Path
from src.hotel.models import Room

def export_bookings_to_json(bookings: list[dict], path: Path) -> None:
    path.write_text(json.dumps(bookings, ensure_ascii=False, indent=2), encoding="utf-8")

def import_rooms_from_csv(path: Path) -> list[Room]:
    rooms = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rooms.append(Room(room_number=row["number"], price=float(row["price"])))
    return rooms