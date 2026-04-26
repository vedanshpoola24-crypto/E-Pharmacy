import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.services.seed import seed_demo_data


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        seed_demo_data()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def token(client):
    response = client.post("/api/auth/login", json={"email": "admin@medstore.local", "password": "Admin@12345"})
    return response.get_json()["access_token"]


@pytest.fixture()
def auth(token):
    return {"Authorization": f"Bearer {token}"}
