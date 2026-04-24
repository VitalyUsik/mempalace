"""Tests for palace.py lifecycle helpers: close_palace and safe_mine_session."""

import os
import signal
from unittest.mock import patch


def test_close_palace_delegates_to_backend(monkeypatch):
    from mempalace import palace

    calls = []
    monkeypatch.setattr(palace._DEFAULT_BACKEND, "close_palace", lambda p: calls.append(p))

    palace.close_palace("/some/path")

    assert calls == ["/some/path"]


def test_safe_mine_session_sets_interrupted_on_sigint():
    from mempalace.palace import safe_mine_session

    with safe_mine_session("/tmp/fake-palace", dry_run=True) as session:
        os.kill(os.getpid(), signal.SIGINT)
        assert session.interrupted


def test_safe_mine_session_restores_signal_handler():
    from mempalace.palace import safe_mine_session

    original = signal.getsignal(signal.SIGINT)
    with safe_mine_session("/tmp/fake-palace", dry_run=True):
        inside = signal.getsignal(signal.SIGINT)
        assert inside != original

    assert signal.getsignal(signal.SIGINT) == original


def test_safe_mine_session_dry_run_skips_close_palace():
    from mempalace.palace import safe_mine_session

    calls = []
    with patch("mempalace.palace.close_palace", side_effect=lambda p: calls.append(p)):
        with safe_mine_session("/tmp/fake-palace", dry_run=True):
            pass

    assert calls == []


def test_safe_mine_session_calls_close_palace_on_exit():
    from mempalace.palace import safe_mine_session

    calls = []
    with patch("mempalace.palace.close_palace", side_effect=lambda p: calls.append(p)):
        with safe_mine_session("/my/palace", dry_run=False):
            pass

    assert calls == ["/my/palace"]


def test_safe_mine_session_double_sigint_prints_warning(capsys):
    from mempalace.palace import safe_mine_session

    with safe_mine_session("/tmp/fake-palace", dry_run=True) as session:
        os.kill(os.getpid(), signal.SIGINT)
        os.kill(os.getpid(), signal.SIGINT)
        assert session.interrupted

    captured = capsys.readouterr()
    assert "Ctrl+C received" in captured.out
    assert "Stopping after this file" in captured.out
