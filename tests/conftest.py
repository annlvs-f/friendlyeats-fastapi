import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def tag():
    """Texto único por prueba: sirve como ciudad para aislar los datos."""
    return "t" + uuid.uuid4().hex[:8]


@pytest.fixture
def make_restaurant(client):
    """Crea restaurantes por la API y los borra al terminar la prueba."""
    created: list[str] = []

    def _make(**overrides) -> dict:
        payload = {"name": "Restaurante Test", "category": "Mexicana", "city": "Puebla", "price": 2}
        payload.update(overrides)
        response = client.post("/api/v1/restaurants", json=payload)
        assert response.status_code == 201, response.text
        data = response.json()
        created.append(data["id"])
        return data

    yield _make

    for restaurant_id in created:
        client.delete(f"/api/v1/restaurants/{restaurant_id}")