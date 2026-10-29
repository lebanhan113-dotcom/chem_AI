from pathlib import Path
from fastapi.testclient import TestClient
import server

ROOT=Path(__file__).resolve().parents[1]

def test_root_index_exists_and_has_author():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    assert '<title>EDUVIDEO FLOW AI V4.2' in html
    assert 'Lê Bá Nhẫn – Trường THPT Hòn Đất' in html
    assert '<style>' in html and '<script>' in html
    assert 'fileModeWarning' in html

def test_server_serves_index_on_both_paths():
    with TestClient(server.app) as client:
        for endpoint in ('/','/index.html'):
            response=client.get(endpoint)
            assert response.status_code==200
            assert 'text/html' in response.headers['content-type']
            assert 'Lê Bá Nhẫn – Trường THPT Hòn Đất' in response.text
