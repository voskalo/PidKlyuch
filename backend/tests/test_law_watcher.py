"""Offline tests for scripts/check_law_updates.py (no network)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_law_updates", Path(__file__).resolve().parents[1] / "scripts" / "check_law_updates.py"
)
watcher = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(watcher)


def test_normalize_and_extract():
    page = "<p>Редакція від 01.11.2026</p><div>A  START text&nbsp;of <b>clause</b> END rest</div>"
    text = watcher.normalize(page)
    assert watcher.revision_of(text) == "01.11.2026"
    assert watcher.extract_clause(text, "START", "END") == "START text of clause"
    assert watcher.extract_clause(text, "NOPE", "END") is None


def test_fingerprint_ignores_markup_but_not_wording():
    a = watcher.fingerprint(watcher.normalize("<p>ставка 50,0</p>"))
    b = watcher.fingerprint(watcher.normalize("<p>ставка   <i>50,0</i></p>"))
    c = watcher.fingerprint(watcher.normalize("<p>ставка 60,0</p>"))
    assert a == b != c


def test_changed_text_is_reported(capsys):
    # A page that contains every marker but different wording -> fingerprints differ -> exit 1
    import json
    sources = json.loads(watcher.RATES_FILE.read_text(encoding="utf-8"))["sources"]
    page = " ".join(f"{s['start']} змінений текст {s['end']}" for s in sources.values() if s.get("start"))
    assert watcher.check(fetch=lambda url: page) == 1
    assert "[CHANGED]" in capsys.readouterr().out


def test_missing_markers_or_network_error_needs_review():
    assert watcher.check(fetch=lambda url: "<html>порожньо</html>") == 2

    def boom(url):
        raise ConnectionError("offline")

    assert watcher.check(fetch=boom) == 2
