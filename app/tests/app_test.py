import os
from unittest.mock import patch

from app.main import app


def test_home_page_loads():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert 'html' in response.get_data(as_text=True).lower()


def test_return_backwards_string():
    client = app.test_client()
    response = client.get('/api/reverse/Hello,%20World!')
    assert response.status_code == 200
    assert response.get_data(as_text=True) == '!dlroW ,olleH'


def test_get_env():
    client = app.test_client()
    with patch.dict(os.environ, {}, clear=True):
        response = client.get('/get-mode')
        assert response.status_code == 200
        assert 'No mode set' in response.get_data(as_text=True)
