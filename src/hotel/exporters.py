import json
import csv
from pathlib import Path

def export_bookings_to_json(bookings: list[dict], path: Path) -> None:
    temp_path = path.with_suffix('.tmp')
    try:
        temp_path.write_text(json.dumps(bookings, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(path) # Атомарна заміна
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

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