import json
import csv
from pathlib import Path

def export_bookings_to_json(bookings: list[dict], path: Path) -> None:
    path.write_text(json.dumps(bookings, ensure_ascii=False, indent=2), encoding="utf-8")

def import_bookings_from_csv(path: Path) -> list[dict]:
    bookings = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bookings.append({
                "booking_id": int(row["id"]),
                "room_number": row["room"],
                "status": row["status"]
            })
    return bookings