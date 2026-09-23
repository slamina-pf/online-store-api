import uuid

from httpx import AsyncClient


async def create_product(client: AsyncClient, **overrides):
    payload = {"title": "Classic Tee", "slug": "classic-tee", "status": "active", "vendor": "Acme"}
    payload.update(overrides)
    return await client.post("/products", json=payload)


async def test_create_product(client: AsyncClient):
    response = await create_product(client)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Classic Tee"
    assert body["slug"] == "classic-tee"
    assert body["options"] == []
    assert body["variants"] == []
    assert body["images"] == []


async def test_create_product_duplicate_slug_conflicts(client: AsyncClient):
    await create_product(client)
    response = await create_product(client, title="Another")
    assert response.status_code == 409


async def test_get_product(client: AsyncClient):
    created = (await create_product(client)).json()
    response = await client.get(f"/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_product_not_found(client: AsyncClient):
    response = await client.get(f"/products/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_list_products_pagination_and_filters(client: AsyncClient):
    await create_product(client, slug="tee-1", vendor="Acme", status="active")
    await create_product(client, slug="tee-2", vendor="Acme", status="draft")
    await create_product(client, slug="tee-3", vendor="Other", status="active")

    response = await client.get("/products", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.get("/products", params={"vendor": "Acme"})
    assert {p["slug"] for p in response.json()} == {"tee-1", "tee-2"}

    response = await client.get("/products", params={"status_filter": "active"})
    assert {p["slug"] for p in response.json()} == {"tee-1", "tee-3"}


async def test_update_product(client: AsyncClient):
    created = (await create_product(client)).json()
    response = await client.patch(f"/products/{created['id']}", json={"vendor": "New Vendor"})
    assert response.status_code == 200
    body = response.json()
    assert body["vendor"] == "New Vendor"
    assert body["updated_at"] != created["updated_at"]


async def test_update_product_duplicate_slug_conflicts(client: AsyncClient):
    await create_product(client, slug="tee-a")
    other = (await create_product(client, slug="tee-b")).json()
    response = await client.patch(f"/products/{other['id']}", json={"slug": "tee-a"})
    assert response.status_code == 409


async def test_delete_product_soft_deletes(client: AsyncClient):
    created = (await create_product(client)).json()
    response = await client.delete(f"/products/{created['id']}")
    assert response.status_code == 204

    response = await client.get(f"/products/{created['id']}")
    assert response.status_code == 404

    response = await client.get("/products")
    assert created["id"] not in {p["id"] for p in response.json()}


async def test_delete_product_not_found(client: AsyncClient):
    response = await client.delete(f"/products/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_create_and_list_product_variant(client: AsyncClient):
    product = (await create_product(client)).json()
    response = await client.post(
        f"/products/{product['id']}/variants",
        json={"sku": "TEE-BLK-M", "price_cents": 2500, "option1": "Black", "option2": "M"},
    )
    assert response.status_code == 201
    variant = response.json()
    assert variant["product_id"] == product["id"]
    assert variant["price_cents"] == 2500

    response = await client.get(f"/products/{product['id']}/variants")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_create_variant_duplicate_sku_conflicts(client: AsyncClient):
    product = (await create_product(client)).json()
    await client.post(f"/products/{product['id']}/variants", json={"sku": "TEE-1", "price_cents": 1000})
    other_product = (await create_product(client, slug="other")).json()
    response = await client.post(
        f"/products/{other_product['id']}/variants", json={"sku": "TEE-1", "price_cents": 1000}
    )
    assert response.status_code == 409


async def test_create_variant_missing_product_returns_404(client: AsyncClient):
    response = await client.post(
        f"/products/{uuid.uuid4()}/variants", json={"sku": "X", "price_cents": 100}
    )
    assert response.status_code == 404


async def test_variant_get_update_delete_by_id(client: AsyncClient):
    product = (await create_product(client)).json()
    variant = (
        await client.post(
            f"/products/{product['id']}/variants", json={"sku": "TEE-2", "price_cents": 1500}
        )
    ).json()

    response = await client.get(f"/products/variants/{variant['id']}")
    assert response.status_code == 200

    response = await client.patch(f"/products/variants/{variant['id']}", json={"price_cents": 1600})
    assert response.status_code == 200
    assert response.json()["price_cents"] == 1600
    assert response.json()["updated_at"] != variant["updated_at"]

    response = await client.delete(f"/products/variants/{variant['id']}")
    assert response.status_code == 204

    response = await client.get(f"/products/variants/{variant['id']}")
    assert response.status_code == 404


async def test_variant_not_found(client: AsyncClient):
    response = await client.get(f"/products/variants/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_create_and_manage_product_option(client: AsyncClient):
    product = (await create_product(client)).json()
    response = await client.post(
        f"/products/{product['id']}/options", json={"name": "Color", "position": 0}
    )
    assert response.status_code == 201
    option = response.json()

    response = await client.get(f"/products/{product['id']}/options")
    assert len(response.json()) == 1

    response = await client.patch(f"/products/options/{option['id']}", json={"name": "Size"})
    assert response.status_code == 200
    assert response.json()["name"] == "Size"

    response = await client.delete(f"/products/options/{option['id']}")
    assert response.status_code == 204

    response = await client.get(f"/products/options/{option['id']}")
    assert response.status_code == 404


async def test_create_and_manage_product_image(client: AsyncClient):
    product = (await create_product(client)).json()
    response = await client.post(
        f"/products/{product['id']}/images", json={"url": "https://example.com/a.png"}
    )
    assert response.status_code == 201
    image = response.json()

    response = await client.get(f"/products/{product['id']}/images")
    assert len(response.json()) == 1

    response = await client.patch(f"/products/images/{image['id']}", json={"alt": "Front"})
    assert response.status_code == 200
    assert response.json()["alt"] == "Front"

    response = await client.delete(f"/products/images/{image['id']}")
    assert response.status_code == 204

    response = await client.get(f"/products/images/{image['id']}")
    assert response.status_code == 404
