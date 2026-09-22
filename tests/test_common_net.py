"""Offline tests for datasets/_common/net.py. A fake HTTP adapter stands in for every provider."""

import hashlib
import io

import pytest
import requests
from requests.adapters import BaseAdapter

from datasets._common import net


class FakeAdapter(BaseAdapter):
    """Serve canned bodies by URL, without any network. Records every request."""

    def __init__(self, routes):
        super().__init__()
        self.routes = routes
        self.requests = []

    def send(self, request, **kwargs):  # noqa: ARG002
        self.requests.append(request)
        base = request.url.split("?")[0]
        body, status, headers, final_url = self.routes[base]
        resp = requests.Response()
        resp.status_code = status
        resp.reason = "OK" if status == 200 else "ERR"
        resp.headers.update(headers)
        resp.raw = io.BytesIO(body)
        resp.url = final_url or request.url
        resp.request = request
        return resp

    def close(self):
        pass


def session_with(routes):
    session = net.make_session()
    adapter = FakeAdapter(routes)
    session.mount("https://", adapter)
    return session, adapter


# --------------------------------------------------------------------------- #
# Credentials
# --------------------------------------------------------------------------- #
def test_load_dotenv_sets_missing_keys_and_keeps_existing(tmp_path, monkeypatch):
    dotenv = tmp_path / ".env"
    dotenv.write_text('# comment\nPWQ_A="alpha"\nPWQ_B=beta\n\nnot a pair\n', encoding="utf-8")
    monkeypatch.delenv("PWQ_A", raising=False)
    monkeypatch.setenv("PWQ_B", "from-shell")
    net.load_dotenv(dotenv)
    assert net.resolve_env("PWQ_A", dotenv) == "alpha"
    assert net.resolve_env("PWQ_B", dotenv) == "from-shell"


def test_resolve_env_treats_empty_as_unset(tmp_path, monkeypatch):
    dotenv = tmp_path / ".env"
    dotenv.write_text("OB_DAAC_EDL_TOKEN=\n", encoding="utf-8")
    monkeypatch.delenv("OB_DAAC_EDL_TOKEN", raising=False)
    assert net.resolve_edl_token(dotenv) is None
    monkeypatch.setenv("OB_DAAC_EDL_TOKEN", "tok")
    assert net.resolve_edl_token(dotenv) == "tok"


def test_load_dotenv_missing_file_is_a_no_op(tmp_path):
    net.load_dotenv(tmp_path / "absent")


# --------------------------------------------------------------------------- #
# Hashing and manifests
# --------------------------------------------------------------------------- #
def test_sha256_file_matches_hashlib(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"abc" * 1000)
    assert net.sha256_file(p) == hashlib.sha256(b"abc" * 1000).hexdigest()


def test_manifest_roundtrip_is_append_only_and_sorted(tmp_path):
    m = tmp_path / "m.jsonl"
    assert net.read_manifest(m) == []
    net.append_manifest(m, {"b": 1, "a": 2})
    net.append_manifest(m, {"c": 3})
    text = m.read_text(encoding="utf-8")
    assert text.splitlines()[0] == '{"a": 2, "b": 1}'
    assert net.read_manifest(m) == [{"a": 2, "b": 1}, {"c": 3}]


# --------------------------------------------------------------------------- #
# Downloads
# --------------------------------------------------------------------------- #
URL = "https://example.invalid/file.tif"
BODY = b"tiff-bytes" * 100
SHA = hashlib.sha256(BODY).hexdigest()


def test_fresh_download_then_cache_hit(tmp_path):
    session, adapter = session_with({URL: (BODY, 200, {"Content-Type": "image/tiff"}, None)})
    dest = tmp_path / "file.tif"
    first = net.download_file(session, URL, dest)
    assert first.cached is False
    assert first.integrity == "unverified"
    assert first.sha256 == SHA
    assert first.bytes == len(BODY)
    assert dest.read_bytes() == BODY
    assert not dest.with_suffix(".tif.part").exists()

    second = net.download_file(session, URL, dest, expected_sha256=SHA)
    assert second.cached is True
    assert second.integrity == "verified"
    assert len(adapter.requests) == 1


def test_stale_cache_is_refetched(tmp_path):
    session, adapter = session_with({URL: (BODY, 200, {}, None)})
    dest = tmp_path / "file.tif"
    dest.write_bytes(b"corrupt bytes on disk")
    result = net.download_file(session, URL, dest, expected_sha256=SHA)
    assert result.cached is False
    assert result.integrity == "refetched_stale_cache"
    assert dest.read_bytes() == BODY
    assert len(adapter.requests) == 1


def test_upstream_change_is_reported_as_mismatch(tmp_path):
    session, _ = session_with({URL: (BODY, 200, {}, None)})
    dest = tmp_path / "file.tif"
    result = net.download_file(session, URL, dest, expected_sha256="0" * 64)
    assert result.integrity == "mismatch"
    assert dest.read_bytes() == BODY


def test_short_body_fails_and_leaves_no_partial(tmp_path):
    session, _ = session_with({URL: (b"", 200, {}, None)})
    dest = tmp_path / "file.tif"
    with pytest.raises(OSError):
        net.download_file(session, URL, dest, min_bytes=1)
    assert not dest.exists()
    assert not dest.with_suffix(".tif.part").exists()


def test_login_landing_page_raises_permission_error(tmp_path):
    html = b"<html>Earthdata Login</html>"
    routes = {
        URL: (html, 200, {"Content-Type": "text/html"}, "https://urs.earthdata.nasa.gov/oauth")
    }
    session, _ = session_with(routes)
    with pytest.raises(PermissionError):
        net.download_file(session, URL, tmp_path / "file.tif")


def test_bearer_token_beats_appkey(tmp_path):
    session, adapter = session_with({URL: (BODY, 200, {}, None)})
    net.download_file(session, URL, tmp_path / "a.tif", appkey="k", bearer_token="t")
    sent = adapter.requests[-1]
    assert sent.headers["Authorization"] == "Bearer t"
    assert "appkey" not in sent.url


def test_appkey_is_a_query_parameter(tmp_path):
    session, adapter = session_with({URL: (BODY, 200, {}, None)})
    net.download_file(session, URL, tmp_path / "a.tif", appkey="k")
    assert adapter.requests[-1].url.endswith("?appkey=k")


def test_user_agent_is_set():
    session = net.make_session()
    assert session.headers["User-Agent"].startswith("public-water-quality-pipeline")
