def test_home_lists_restaurants(client, make_restaurant, tag):
    make_restaurant(name="Tacos del Centro", city=tag, category="Tacos", price=1)
    response = client.get("/", params={"city": tag})
    assert response.status_code == 200
    assert "Tacos del Centro" in response.text
    assert "Ver detalles" in response.text


def test_home_empty_state(client, tag):
    response = client.get("/", params={"city": tag})
    assert response.status_code == 200
    assert "No hay restaurantes" in response.text


def test_detail_page(client, make_restaurant):
    created = make_restaurant(name="Casa Detalle", price=3)
    response = client.get(f"/restaurants/{created['id']}")
    assert response.status_code == 200
    assert "Casa Detalle" in response.text
    assert "Editar" in response.text and "Eliminar" in response.text


def test_detail_page_not_found(client):
    response = client.get("/restaurants/no-existe")
    assert response.status_code == 404
    assert "Restaurante no encontrado" in response.text


def test_new_form(client):
    response = client.get("/restaurants/new")
    assert response.status_code == 200
    assert "Nuevo restaurante" in response.text


def test_edit_form_is_prefilled(client, make_restaurant):
    created = make_restaurant(name="Para Editar", price=3)
    response = client.get(f"/restaurants/{created['id']}/edit")
    assert response.status_code == 200
    assert "Editar restaurante" in response.text
    assert 'value="Para Editar"' in response.text
    assert 'value="3" selected' in response.text