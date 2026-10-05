from src.hotel.config import get_allowed_statuses

def test_allowed_statuses_default(monkeypatch):
    monkeypatch.delenv("ALLOWED_STATUSES", raising=False)
    assert get_allowed_statuses() == ["pending", "confirmed", "cancelled"]

def test_allowed_statuses_custom(monkeypatch):
    monkeypatch.setenv("ALLOWED_STATUSES", "active, archived")
    assert get_allowed_statuses() == ["active", "archived"]