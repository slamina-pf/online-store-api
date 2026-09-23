from fastapi import FastAPI

from online_store_api.api.routers import collections, products

app = FastAPI(title="online-store-api")

app.include_router(products.router)
app.include_router(collections.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
