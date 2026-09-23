import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from online_store_api.api.deps import get_db
from online_store_api.models.product import Collection, CollectionProduct, Product
from online_store_api.schemas.collection import (
    CollectionCreate,
    CollectionProductAdd,
    CollectionProductRead,
    CollectionRead,
    CollectionUpdate,
)
from online_store_api.schemas.common import Pagination
from online_store_api.schemas.product import ProductSummary

router = APIRouter(prefix="/collections", tags=["collections"])


async def get_collection_or_404(db: AsyncSession, collection_id: uuid.UUID) -> Collection:
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()
    if collection is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Collection not found")
    return collection


@router.post("", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
async def create_collection(
    payload: CollectionCreate, db: AsyncSession = Depends(get_db)
) -> Collection:
    collection = Collection(**payload.model_dump())
    db.add(collection)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Collection slug already exists") from exc
    return collection


@router.get("", response_model=list[CollectionRead])
async def list_collections(
    pagination: Pagination = Depends(), db: AsyncSession = Depends(get_db)
) -> list[Collection]:
    result = await db.execute(
        select(Collection)
        .order_by(Collection.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    return list(result.scalars().all())


@router.get("/{collection_id}", response_model=CollectionRead)
async def get_collection(collection_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Collection:
    return await get_collection_or_404(db, collection_id)


@router.patch("/{collection_id}", response_model=CollectionRead)
async def update_collection(
    collection_id: uuid.UUID, payload: CollectionUpdate, db: AsyncSession = Depends(get_db)
) -> Collection:
    collection = await get_collection_or_404(db, collection_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(collection, field, value)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Collection slug already exists") from exc
    await db.refresh(collection, attribute_names=["updated_at"])
    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(collection_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    collection = await get_collection_or_404(db, collection_id)
    await db.delete(collection)
    await db.commit()


@router.post(
    "/{collection_id}/products",
    response_model=CollectionProductRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_collection_product(
    collection_id: uuid.UUID, payload: CollectionProductAdd, db: AsyncSession = Depends(get_db)
) -> CollectionProduct:
    await get_collection_or_404(db, collection_id)
    product_result = await db.execute(
        select(Product).where(Product.id == payload.product_id, Product.deleted_at.is_(None))
    )
    product = product_result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")

    link = CollectionProduct(
        collection_id=collection_id, product_id=payload.product_id, position=payload.position
    )
    db.add(link)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Product already in collection"
        ) from exc
    return CollectionProductRead(product=ProductSummary.model_validate(product), position=link.position)


@router.get("/{collection_id}/products", response_model=list[CollectionProductRead])
async def list_collection_products(
    collection_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[CollectionProductRead]:
    await get_collection_or_404(db, collection_id)
    result = await db.execute(
        select(Product, CollectionProduct.position)
        .join(CollectionProduct, CollectionProduct.product_id == Product.id)
        .where(CollectionProduct.collection_id == collection_id, Product.deleted_at.is_(None))
        .order_by(CollectionProduct.position)
    )
    return [
        CollectionProductRead(product=ProductSummary.model_validate(product), position=position)
        for product, position in result.all()
    ]


@router.delete("/{collection_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_collection_product(
    collection_id: uuid.UUID, product_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    result = await db.execute(
        select(CollectionProduct).where(
            CollectionProduct.collection_id == collection_id,
            CollectionProduct.product_id == product_id,
        )
    )
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not in collection")
    await db.delete(link)
    await db.commit()
