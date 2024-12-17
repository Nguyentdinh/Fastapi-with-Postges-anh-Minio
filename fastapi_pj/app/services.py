from typing import TYPE_CHECKING, List

import database as _database
import models as _models
import schemas as _schemas

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_product(
    product: _schemas.CreateProduct, db: "Session"
) -> _schemas.Product:
    product = _models.Product(**product.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return _schemas.Product.from_orm(product)


async def get_all_Product(db: "Session") -> List[_schemas.Product]:
    products = db.query(_models.Product).all()
    return list(map(_schemas.Product.from_orm, products))


async def get_product(product_id: int, db: "Session"):
    product = db.query(_models.Product).filter(_models.Product.id == product_id).first()
    return product


async def delete_product(product: _models.Product, db: "Session"):
    db.delete(product)
    db.commit()


async def update_product(
    product_data: _schemas.CreateProduct, product: _models.Product, db: "Session"
) -> _schemas.Product:
    product.title = product_data.title
    product.link = product_data.link
    product.discount = product_data.discount
    product.sales = product_data.sales
    product.paths_minio = product_data.paths_minio

    db.commit()
    db.refresh(product)

    return _schemas.Product.from_orm(product)
from sqlalchemy.orm import Session
from models import Product

async def create_product(product_data: dict, db: "Session"):
    # Chèn dữ liệu vào bảng Product
    new_product = Product(**product_data)  # Sử dụng unpacking để truyền dict vào model
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product
