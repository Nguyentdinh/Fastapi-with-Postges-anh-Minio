import datetime as _dt
import pydantic as _pydantic


class _BaseProduct(_pydantic.BaseModel):
    title: str
    link: str
    discount: str
    sales: str
    paths_minio: str


class Product(_BaseProduct):
    id: int
   

    class Config:
        orm_mode = True


class CreateProduct(_BaseProduct):
    pass
