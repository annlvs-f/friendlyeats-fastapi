from app.core.firebase import get_db

API = "/api/v1/restaurants"


# ---------------------------------------------------------------- salud
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------- crear (HU-01)
def test_create_restaurant(client, make_restaurant):
    data = make_restaurant(name="La Prueba")
    assert data["id"]
    assert data["name"] == "La Prueba"
    assert data["avgRating"] == 0
    assert data["numRatings"] == 0


def test_create_ignores_client_ratings(make_restaurant):
    data = make_restaurant(avgRating=5, numRatings=999)
    assert data["avgRating"] == 0
    assert data["numRatings"] == 0


def test_create_trims_spaces(make_restaurant):
    assert make_restaurant(name="  La Abuela  ")["name"] == "La Abuela"


def test_invalid_price(client):
    for price in (10, 0, -1):
        payload = {"name": "X", "category": "Mexicana", "city": "Puebla", "price": price}
        assert client.post(API, json=payload).status_code == 422


def test_invalid_fields(client):
    base = {"name": "X", "category": "Mexicana", "city": "Puebla", "price": 2}
    assert client.post(API, json={**base, "name": ""}).status_code == 422
    assert client.post(API, json={**base, "name": "x" * 101}).status_code == 422
    assert client.post(API, json={**base, "price": "caro"}).status_code == 422
    assert client.post(API, json={**base, "photoUrl": "no-es-url"}).status_code == 422
    sin_ciudad = {k: v for k, v in base.items() if k != "city"}
    assert client.post(API, json=sin_ciudad).status_code == 422


# ---------------------------------------------------------------- obtener (HU-03)
def test_get_restaurant(client, make_restaurant):
    created = make_restaurant(name="Detalle")
    response = client.get(f"{API}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Detalle"


def test_get_restaurant_not_found(client):
    response = client.get(f"{API}/no-existe")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurante no encontrado"


# ---------------------------------------------------------------- listar y filtros (HU-02)
def test_list_filters(client, make_restaurant, tag):
    make_restaurant(name="A", city=tag, category="Pizza", price=1)
    make_restaurant(name="B", city=tag, category="Pizza", price=3)
    make_restaurant(name="C", city=tag, category="Tacos", price=1)

    def names(**params):
        response = client.get(API, params=params)
        assert response.status_code == 200
        return [r["name"] for r in response.json()]

    assert names(city=tag) == ["A", "B", "C"]
    assert names(city=tag, category="Pizza") == ["A", "B"]
    assert names(city=tag, price=1) == ["A", "C"]
    assert names(city=tag, category="Pizza", price=3) == ["B"]
    assert names(city="no-existe-" + tag) == []


def test_list_pagination(client, make_restaurant, tag):
    for letter in "ABCDE":
        make_restaurant(name=letter, city=tag)

    page1 = client.get(API, params={"city": tag, "limit": 2}).json()
    assert [r["name"] for r in page1] == ["A", "B"]

    page2 = client.get(API, params={"city": tag, "limit": 2, "start_after": page1[-1]["id"]}).json()
    assert [r["name"] for r in page2] == ["C", "D"]


def test_list_order_by_rating(client, make_restaurant, tag):
    bajo = make_restaurant(name="Bajo", city=tag)
    alto = make_restaurant(name="Alto", city=tag)
    coleccion = get_db().collection("restaurants")
    coleccion.document(bajo["id"]).update({"avgRating": 2.0, "numRatings": 3})
    coleccion.document(alto["id"]).update({"avgRating": 4.8, "numRatings": 9})

    response = client.get(API, params={"city": tag, "order_by": "avgRating"})
    assert [r["name"] for r in response.json()] == ["Alto", "Bajo"]


def test_list_invalid_params(client):
    assert client.get(API, params={"order_by": "price"}).status_code == 422
    assert client.get(API, params={"price": 9}).status_code == 422
    assert client.get(API, params={"limit": 0}).status_code == 422
    assert client.get(API, params={"limit": 101}).status_code == 422


# ---------------------------------------------------------------- editar (HU-04)
def test_update_only_sent_fields(client, make_restaurant):
    created = make_restaurant(name="Original", category="Pizza", price=1)
    response = client.patch(f"{API}/{created['id']}", json={"price": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 3
    assert data["name"] == "Original"
    assert data["category"] == "Pizza"


def test_update_not_found(client):
    assert client.patch(f"{API}/no-existe", json={"price": 2}).status_code == 404


def test_update_without_fields_is_400(client, make_restaurant):
    created = make_restaurant()
    assert client.patch(f"{API}/{created['id']}", json={}).status_code == 400


def test_update_cannot_change_protected_fields(client, make_restaurant):
    created = make_restaurant()
    response = client.patch(f"{API}/{created['id']}", json={"avgRating": 5, "numRatings": 100})
    assert response.status_code == 400
    assert client.get(f"{API}/{created['id']}").json()["avgRating"] == 0


def test_update_validations(client, make_restaurant):
    created = make_restaurant()
    url = f"{API}/{created['id']}"
    assert client.patch(url, json={"price": 10}).status_code == 422
    assert client.patch(url, json={"name": ""}).status_code == 422
    assert client.patch(url, json={"name": None}).status_code == 422


# ---------------------------------------------------------------- eliminar (HU-05)
def test_delete_restaurant(client, make_restaurant):
    created = make_restaurant()
    response = client.delete(f"{API}/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"{API}/{created['id']}").status_code == 404


def test_delete_not_found(client):
    assert client.delete(f"{API}/no-existe").status_code == 404