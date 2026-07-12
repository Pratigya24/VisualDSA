import asyncio
import subprocess

import pytest

from app.core.config import get_settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def monkeypatch_session():
    """Session-scoped equivalent of pytest's function-scoped `monkeypatch`."""
    from _pytest.monkeypatch import MonkeyPatch

    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture(scope="session", autouse=True)
def rsa_test_keys(tmp_path_factory, monkeypatch_session):
    """Generates a throwaway RSA keypair for the test session and points
    Settings at it, so JWT tests never touch real credentials.
    """
    keys_dir = tmp_path_factory.mktemp("keys")
    private_key = keys_dir / "private.pem"
    public_key = keys_dir / "public.pem"

    subprocess.run(["openssl", "genrsa", "-out", str(private_key), "2048"], check=True, capture_output=True)
    subprocess.run(
        ["openssl", "rsa", "-in", str(private_key), "-pubout", "-out", str(public_key)],
        check=True,
        capture_output=True,
    )

    monkeypatch_session.setenv("JWT_PRIVATE_KEY_PATH", str(private_key))
    monkeypatch_session.setenv("JWT_PUBLIC_KEY_PATH", str(public_key))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
