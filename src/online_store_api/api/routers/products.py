import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from online_store_api.api.deps import get_db
from online_store_api.models.product import Product, ProductImage, ProductOption, ProductVariant
from online_store_api.schemas.common import Pagination
from online_store_api.schemas.product import (
    ProductCreate,
    ProductImageCreate,
    ProductImageRead,
    ProductImageUpdate,
    ProductOptionCreate,
    ProductOptionRead,
    ProductRead,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantRead,
    ProductVariantUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])

PRODUCT_LOAD_OPTIONS = (
    selectinload(Product.options),
    selectinload(Product.variants),
    selectinload(Product.images),
)


async def get_product_or_404(db: AsyncSession, product_id: uuid.UUID) -> Product:
    result = await db.execute(
        select(Product)
        .options(*PRODUCT_LOAD_OPTIONS)
        .where(Product.id == product_id, Product.deleted_at.is_(None))
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return product


async def ensure_product_exists(db: AsyncSession, product_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Product.id).where(Product.id == product_id, Product.deleted_at.is_(None))
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Product slug already exists") from exc
    await db.refresh(product, attribute_names=["options", "variants", "images"])
    return product


@router.get("", response_model=list[ProductRead])
async def list_products(
    pagination: Pagination = Depends(),
    status_filter: str | None = None,
    vendor: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Product]:
    query = select(Product).options(*PRODUCT_LOAD_OPTIONS).where(Product.deleted_at.is_(None))
    if status_filter is not None:
        query = query.where(Product.status == status_filter)
    if vendor is not None:
        query = query.where(Product.vendor == vendor)
    query = query.order_by(Product.created_at.desc()).offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Product:
    return await get_product_or_404(db, product_id)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: uuid.UUID, payload: ProductUpdate, db: AsyncSession = Depends(get_db)
) -> Product:
    product = await get_product_or_404(db, product_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Product slug already exists") from exc
    await db.refresh(product, attribute_names=["updated_at", "options", "variants", "images"])
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    product = await get_product_or_404(db, product_id)
    product.deleted_at = datetime.now(UTC)
    await db.commit()


@router.post(
    "/{product_id}/options", response_model=ProductOptionRead, status_code=status.HTTP_201_CREATED
)
async def create_product_option(
    product_id: uuid.UUID, payload: ProductOptionCreate, db: AsyncSession = Depends(get_db)
) -> ProductOption:
    await ensure_product_exists(db, product_id)
    option = ProductOption(product_id=product_id, **payload.model_dump())
    db.add(option)
    await db.commit()
    return option


@router.get("/{product_id}/options", response_model=list[ProductOptionRead])
async def list_product_options(
    product_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[ProductOption]:
    await ensure_product_exists(db, product_id)
    result = await db.execute(
        select(ProductOption)
        .where(ProductOption.product_id == product_id)
        .order_by(ProductOption.position)
    )
    return list(result.scalars().all())


@router.post(
    "/{product_id}/variants",
    response_model=ProductVariantRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_variant(
    product_id: uuid.UUID, payload: ProductVariantCreate, db: AsyncSession = Depends(get_db)
) -> ProductVariant:
    await ensure_product_exists(db, product_id)
    variant = ProductVariant(product_id=product_id, **payload.model_dump())
    db.add(variant)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Variant SKU already exists") from exc
    return variant


@router.get("/{product_id}/variants", response_model=list[ProductVariantRead])
async def list_product_variants(
    product_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[ProductVariant]:
    await ensure_product_exists(db, product_id)
    result = await db.execute(
        select(ProductVariant)
        .where(ProductVariant.product_id == product_id)
        .order_by(ProductVariant.position)
    )
    return list(result.scalars().all())


@router.post(
    "/{product_id}/images", response_model=ProductImageRead, status_code=status.HTTP_201_CREATED
)
async def create_product_image(
    product_id: uuid.UUID, payload: ProductImageCreate, db: AsyncSession = Depends(get_db)
) -> ProductImage:
    await ensure_product_exists(db, product_id)
    image = ProductImage(product_id=product_id, **payload.model_dump())
    db.add(image)
    await db.commit()
    return image


@router.get("/{product_id}/images", response_model=list[ProductImageRead])
async def list_product_images(
    product_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[ProductImage]:
    await ensure_product_exists(db, product_id)
    result = await db.execute(
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.position)
    )
    return list(result.scalars().all())


@router.get("/variants/{variant_id}", response_model=ProductVariantRead)
async def get_variant(variant_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ProductVariant:
    result = await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
    variant = result.scalar_one_or_none()
    if variant is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Variant not found")
    return variant


@router.patch("/variants/{variant_id}", response_model=ProductVariantRead)
async def update_variant(
    variant_id: uuid.UUID, payload: ProductVariantUpdate, db: AsyncSession = Depends(get_db)
) -> ProductVariant:
    variant = await get_variant(variant_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(variant, field, value)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Variant SKU already exists") from exc
    await db.refresh(variant, attribute_names=["updated_at"])
    return variant


@router.delete("/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variant(variant_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    variant = await get_variant(variant_id, db)
    await db.delete(variant)
    await db.commit()


@router.get("/options/{option_id}", response_model=ProductOptionRead)
async def get_option(option_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ProductOption:
    result = await db.execute(select(ProductOption).where(ProductOption.id == option_id))
    option = result.scalar_one_or_none()
    if option is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Option not found")
    return option


@router.patch("/options/{option_id}", response_model=ProductOptionRead)
async def update_option(
    option_id: uuid.UUID, payload: ProductOptionCreate, db: AsyncSession = Depends(get_db)
) -> ProductOption:
    option = await get_option(option_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(option, field, value)
    await db.commit()
    return option


@router.delete("/options/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_option(option_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    option = await get_option(option_id, db)
    await db.delete(option)
    await db.commit()


@router.get("/images/{image_id}", response_model=ProductImageRead)
async def get_image(image_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ProductImage:
    result = await db.execute(select(ProductImage).where(ProductImage.id == image_id))
    image = result.scalar_one_or_none()
    if image is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image not found")
    return image


@router.patch("/images/{image_id}", response_model=ProductImageRead)
async def update_image(
    image_id: uuid.UUID, payload: ProductImageUpdate, db: AsyncSession = Depends(get_db)
) -> ProductImage:
    image = await get_image(image_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(image, field, value)
    await db.commit()
    return image


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    image = await get_image(image_id, db)
    await db.delete(image)
    await db.commit()
