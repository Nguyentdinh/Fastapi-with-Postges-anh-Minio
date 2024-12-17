from typing import List
from fastapi import APIRouter, File, UploadFile, Path, HTTPException, Depends,status
from pydantic import BaseModel
from io import BytesIO
from starlette.responses import StreamingResponse
import sqlalchemy.orm as _orm
import schemas as _schemas
import services as _services
from minio_handler import MinioHandler
from .auth import get_current_user
import csv
from sqlalchemy.exc import IntegrityError
from io import StringIO
# Khởi tạo ứng dụng FastAPI
router = APIRouter()


# PostgreSQL routes
@router.post("/api/product/", response_model=_schemas.Product)
async def create_product(
    product: _schemas.CreateProduct,
    user: dict = Depends(get_current_user),
    db: _orm.Session = Depends(_services.get_db),
):
    allowed_users = ['admin', 'user1', 'user2']
    if user['role'] not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    product_data = product.dict() 
    product_data['owner_id'] = user.get('id')

    return await _services.create_product(product=product, db=db)

@router.get("/api/products/", response_model=List[_schemas.Product])
async def get_all_products(
    user: dict = Depends(get_current_user), 
    db: _orm.Session = Depends(_services.get_db)
):
    allowed_users = ['admin', 'user1', 'user2']
    if user['role'] not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    products = await _services.get_all_products(db=db)
    return products



@router.get("/api/product/{product_id}/", response_model=_schemas.Product)
async def get_product(
    product_id: int,
    user: dict = Depends(get_current_user), 
    db: _orm.Session = Depends(_services.get_db)
):
    allowed_users = ['admin', 'user1', 'user2']
    if user['role'] not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    product = await _services.get_product(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product does not exist")
    return product

@router.put("/api/products/upload")
async def upload_products_from_csv(
    file: UploadFile = File(...), 
    user: dict = Depends(get_current_user), 
    db: _orm.Session = Depends(_services.get_db)
):
    allowed_users = ['admin', 'user1', 'user2']
    if user['role'] not in allowed_users:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    
    try:
        contents = await file.read()
        csv_file = StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            product_data = {
                "title": row.get("title", "default_title"),  # Nếu thiếu title, gán giá trị mặc định
                "price": row.get("price"),  # Nếu thiếu giá, gán giá trị mặc định
                "link": row.get("link", ""),  # Nếu thiếu link, gán giá trị mặc định là chuỗi rỗng
                "discount": row.get("discount"),  # Nếu thiếu discount, gán giá trị mặc định 0.0
                "sales": row.get("sale", 0),  # Nếu thiếu sales, gán giá trị mặc định 0
                "owner_id": user.get("id", None),  # Gán owner_id từ user hiện tại
                "paths_minio": "",  # Giá trị này có thể bỏ trống, sẽ được cập nhật sau khi upload lên Minio
            }
            
            await _services.create_product(product_data, db)

        return {"message": "Products uploaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.delete("/api/product/{product_id}/")
async def delete_product(
    product_id: int,
    user: dict = Depends(get_current_user), 
    db: _orm.Session = Depends(_services.get_db)
):
    allowed_users = ['admin', 'user3', 'user2']
    if user['role'] not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    product = await _services.get_product(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product does not exist")

    await _services.delete_product(product, db=db)
    return "successfully deleted the product"


@router.put("/api/product/{product_id}/", response_model=_schemas.Product)
async def update_product(
    product_id: int,
    product_data: _schemas.CreateProduct,
    user: dict = Depends(get_current_user),
    db: _orm.Session = Depends(_services.get_db),
):
    allowed_users = ['admin', 'user3', 'user2']
    if user['role'] not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    product = await _services.get_product(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product does not exist")

    return await _services.update_product(
        product_data=product_data, product=product, db=db
    )


# Minio routes
class CustomException(Exception):
    http_code: int
    code: str
    message: str

    def __init__(self, http_code: int = None, code: str = None, message: str = None):
        self.http_code = http_code if http_code else 500
        self.code = code if code else str(self.http_code)
        self.message = message


class UploadFileResponse(BaseModel):
    bucket_name: str
    file_name: str
    url: str


@router.post("/upload/minio", response_model=UploadFileResponse)
async def upload_file_to_minio(file: UploadFile = File(...),user: dict = Depends(get_current_user)):
    allowed_users = ['admin', 'user4', 'user5']
    if user['role'] not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    try:
        data = file.file.read()

        file_name = " ".join(file.filename.strip().split())

        data_file = MinioHandler().get_instance().put_object(
            file_name=file_name,
            file_data=BytesIO(data),
            content_type=file.content_type
        )
        return data_file
    except CustomException as e:
        raise e
    except Exception as e:
        if e.__class__.__name__ == 'MaxRetryError':
            raise CustomException(http_code=400, code='400', message='Can not connect to Minio')
        raise CustomException(code='999', message='Server Error')


@router.get("/download/minio/{filePath}")
def download_file_from_minio(*, filePath: str = Path(..., title="The relative path to the file", min_length=1, max_length=500)
            ,user: dict = Depends(get_current_user)):
    allowed_users = ['admin', 'user4', 'user5']
    if user['role'] not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    try:
        minio_client = MinioHandler().get_instance()
        if not minio_client.check_file_name_exists(minio_client.bucket_name, filePath):
            raise CustomException(http_code=400, code='400',
                                  message='File not exists')

        file = minio_client.client.get_object(minio_client.bucket_name, filePath).read()
        return StreamingResponse(BytesIO(file))
    except CustomException as e:
        raise e
    except Exception as e:
        if e.__class__.__name__ == 'MaxRetryError':
            raise CustomException(http_code=400, code='400', message='Can not connect to Minio')
        raise CustomException(code='999', message='Server Error')


@router.get('/')
def root():
    return {"message": "FastAPI app with PostgreSQL and Minio"}
