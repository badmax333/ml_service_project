import time

import pytest

from src.services import captcha_service


def test_generate_captcha_and_verify_success(monkeypatch):
    # make generation deterministic
    monkeypatch.setattr(captcha_service.random, "randint", lambda a, b: 10)
    monkeypatch.setattr(captcha_service.random, "choice", lambda seq: "+")
    monkeypatch.setattr(captcha_service.random, "random", lambda: 0.123)
    monkeypatch.setattr(captcha_service.time, "time", lambda: 1_000.0)

    captcha_id, question, ttl = captcha_service.generate_captcha()
    assert ttl == 300
    assert question == "10 + 10 = ?"
    assert captcha_service.verify_captcha(captcha_id, 20) is True

    # already consumed
    assert captcha_service.verify_captcha(captcha_id, 20) is False


def test_verify_captcha_wrong_answer(monkeypatch):
    monkeypatch.setattr(captcha_service.random, "randint", lambda a, b: 7)
    monkeypatch.setattr(captcha_service.random, "choice", lambda seq: "+")
    monkeypatch.setattr(captcha_service.random, "random", lambda: 0.2)
    monkeypatch.setattr(captcha_service.time, "time", lambda: 2_000.0)

    captcha_id, _, _ = captcha_service.generate_captcha()
    assert captcha_service.verify_captcha(captcha_id, 999) is False


def test_verify_captcha_expired(monkeypatch):
    monkeypatch.setattr(captcha_service.random, "randint", lambda a, b: 20)
    monkeypatch.setattr(captcha_service.random, "choice", lambda seq: "-")
    monkeypatch.setattr(captcha_service.random, "random", lambda: 0.3)

    # generate at time T
    monkeypatch.setattr(captcha_service.time, "time", lambda: 10_000.0)
    captcha_id, _, _ = captcha_service.generate_captcha()

    # verify after expiry (T + 301)
    monkeypatch.setattr(captcha_service.time, "time", lambda: 10_301.0)
    assert captcha_service.verify_captcha(captcha_id, 0) is False


def test_cleanup_expired_captchas(monkeypatch):
    # prepare store with 2 captchas
    captcha_service._captcha_store.clear()
    captcha_service._captcha_store["alive"] = (1, 1_100.0)
    captcha_service._captcha_store["dead"] = (1, 900.0)

    monkeypatch.setattr(captcha_service.time, "time", lambda: 1_000.0)
    captcha_service.cleanup_expired_captchas()

    assert "dead" not in captcha_service._captcha_store
    assert "alive" in captcha_service._captcha_store


@pytest.fixture(autouse=True)
def _cleanup_store():
    yield
    captcha_service._captcha_store.clear()

