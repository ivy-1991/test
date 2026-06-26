from datetime import datetime
from app.services.archive import classify, target_path, RETRY_MINUTES


def test_classify_common_files():
    assert classify("a.mp4") == "video"
    assert classify("b.pdf") == "document"
    assert classify("c.unknown") == "other"


def test_target_path_contains_template_parts(monkeypatch):
    monkeypatch.setattr("app.services.archive.settings.download_root", "/tmp/downloads")
    path = target_path("bad/name", datetime(2026, 6, 24), "movie.mkv")
    assert str(path).endswith("bad_name/2026/06/video/movie.mkv")


def test_retry_schedule_is_permanent_capped():
    assert RETRY_MINUTES == [1, 5, 15, 30, 60]
