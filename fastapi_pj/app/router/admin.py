from typing import List
from fastapi import APIRouter,status, File, UploadFile, Path, HTTPException, Depends
import sqlalchemy.orm as _orm
import database as _database
from models import Product
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/admin/api/products")
async def get_all_products(user: dict = Depends(get_current_user), db: _orm.Session = Depends(get_db)):
    if user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    products = db.query(Product).all()
    return products