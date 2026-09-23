import uuid

from httpx import AsyncClient


async def create_collection(client: AsyncClient, **overrides):
    payload = {"title": "Summer", "slug": "summer"}
    payload.update(overrides)
    return await client.post("/collections", json=payload)


async def create_product(client: AsyncClient, **overrides):
    payload = {"title": "Classic Tee", "slug": "classic-tee", "status": "active"}
    payload.update(overrides)
    return await client.post("/products", json=payload)


async def test_create_collection(client: AsyncClient):
    response = await create_collection(client)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Summer"
    assert body["slug"] == "summer"


async def test_create_collection_duplicate_slug_conflicts(client: AsyncClient):
    await create_collection(client)
    response = await create_collection(client, title="Other")
    assert response.status_code == 409


async def test_get_collection_not_found(client: AsyncClient):
    response = await client.get(f"/collections/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_list_collections(client: AsyncClient):
    await create_collection(client, slug="a")
    await create_collection(client, slug="b")
    response = await client.get("/collections")
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_update_collection(client: AsyncClient):
    created = (await create_collection(client)).json()
    response = await client.patch(f"/collections/{created['id']}", json={"title": "Summer 2026"})
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Summer 2026"
    assert body["updated_at"] != created["updated_at"]


async def test_update_collection_duplicate_slug_conflicts(client: AsyncClient):
    await create_collection(client, slug="a")
    other = (await create_collection(client, slug="b")).json()
    response = await client.patch(f"/collections/{other['id']}", json={"slug": "a"})
    assert response.status_code == 409


async def test_delete_collection(client: AsyncClient):
    created = (await create_collection(client)).json()
    response = await client.delete(f"/collections/{created['id']}")
    assert response.status_code == 204
    response = await client.get(f"/collections/{created['id']}")
    assert response.status_code == 404


async def test_delete_collection_not_found(client: AsyncClient):
    response = await client.delete(f"/collections/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_add_product_to_collection(client: AsyncClient):
    collection = (await create_collection(client)).json()
    product = (await create_product(client)).json()

    response = await client.post(
        f"/collections/{collection['id']}/products",
        json={"product_id": product["id"], "position": 0},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["product"]["id"] == product["id"]
    assert body["position"] == 0


async def test_add_product_to_collection_duplicate_conflicts(client: AsyncClient):
    collection = (await create_collection(client)).json()
    product = (await create_product(client)).json()
    payload = {"product_id": product["id"], "position": 0}

    await client.post(f"/collections/{collection['id']}/products", json=payload)
    response = await client.post(f"/collections/{collection['id']}/products", json=payload)
    assert response.status_code == 409


async def test_add_nonexistent_product_to_collection_returns_404(client: AsyncClient):
    collection = (await create_collection(client)).json()
    response = await client.post(
        f"/collections/{collection['id']}/products",
        json={"product_id": str(uuid.uuid4()), "position": 0},
    )
    assert response.status_code == 404


async def test_list_collection_products_ordered_by_position(client: AsyncClient):
    collection = (await create_collection(client)).json()
    product_a = (await create_product(client, slug="a")).json()
    product_b = (await create_product(client, slug="b")).json()

    await client.post(
        f"/collections/{collection['id']}/products",
        json={"product_id": product_b["id"], "position": 1},
    )
    await client.post(
        f"/collections/{collection['id']}/products",
        json={"product_id": product_a["id"], "position": 0},
    )

    response = await client.get(f"/collections/{collection['id']}/products")
    assert response.status_code == 200
    assert [entry["product"]["slug"] for entry in response.json()] == ["a", "b"]


async def test_remove_product_from_collection(client: AsyncClient):
    collection = (await create_collection(client)).json()
    product = (await create_product(client)).json()
    await client.post(
        f"/collections/{collection['id']}/products",
        json={"product_id": product["id"], "position": 0},
    )

    response = await client.delete(f"/collections/{collection['id']}/products/{product['id']}")
    assert response.status_code == 204

    response = await client.get(f"/collections/{collection['id']}/products")
    assert response.json() == []


async def test_remove_product_not_in_collection_returns_404(client: AsyncClient):
    collection = (await create_collection(client)).json()
    response = await client.delete(f"/collections/{collection['id']}/products/{uuid.uuid4()}")
    assert response.status_code == 404
