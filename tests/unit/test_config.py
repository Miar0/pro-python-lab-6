import os
import datetime
from unittest.mock import patch
from src.hotel.config import get_allowed_statuses, get_current_date


def test_allowed_statuses_default(monkeypatch):
    monkeypatch.delenv("ALLOWED_STATUSES", raising=False)
    assert get_allowed_statuses() == ["pending", "confirmed", "cancelled"]


def test_allowed_statuses_custom(monkeypatch):
    monkeypatch.setenv("ALLOWED_STATUSES", "active, archived")
    assert get_allowed_statuses() == ["active", "archived"]


def test_mocking_os_getenv_with_setattr(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d: "mocked,status")
    assert get_allowed_statuses() == ["mocked", "status"]


@patch("src.hotel.config.os.getenv")
def test_config_with_patch(mock_getenv):
    mock_getenv.return_value = "patched,status"
    assert get_allowed_statuses() == ["patched", "status"]
    mock_getenv.assert_called_once_with("ALLOWED_STATUSES", "pending,confirmed,cancelled")


def test_deterministic_time(monkeypatch):
    """Deterministic time через monkeypatch (Завдання підвищеної складності)."""

    class MockDate:
        @classmethod
        def today(cls):
            return datetime.date(2026, 1, 1)

    monkeypatch.setattr(datetime, "date", MockDate)
    assert get_current_date() == "2026-01-01"