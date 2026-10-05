import json
import csv
from pathlib import Path
from typing import Iterator

def export_bookings_to_json(bookings: list[dict], path: Path) -> None:
    temp_path = path.with_suffix('.tmp')
    try:
        temp_path.write_text(json.dumps(bookings, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(path) # Атомарна заміна
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

def import_bookings_from_csv(path: Path) -> Iterator[dict]:
    """Streaming import через yield."""
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {
                "booking_id": int(row["id"]),
                "room_number": row["room"],
                "status": row["status"]
            }