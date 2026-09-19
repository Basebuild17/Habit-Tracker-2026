import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test",
        "DATABASE": tmp_path / "test.sqlite",
    })


@pytest.fixture()
def client(app):
    return app.test_client()