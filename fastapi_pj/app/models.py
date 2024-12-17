# models.py
import datetime as _dt
import sqlalchemy as _sql

import database as _database

class User(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    first_name = _sql.Column(_sql.String, index=True)
    last_name = _sql.Column(_sql.String, index=True)
    user_name =_sql.Column(_sql.String, unique=True)
    hashed_password = _sql.Column(_sql.String, index=True)
    is_active = _sql.Column(_sql.String, default= True )
    email = _sql.Column(_sql.String, index=True, unique=True)
    role = _sql.Column(_sql.String, index=True, unique=True)
    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)

class Product(_database.Base):
    __tablename__ = "product"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    title = _sql.Column(_sql.String, index=True)
    price = _sql.Column(_sql.String, index=True)
    link =_sql.Column(_sql.String)
    discount = _sql.Column(_sql.String, index=True)
    sales = _sql.Column(_sql.String, index= True )
    paths_minio = _sql.Column(_sql.String, nullable=True)
    owner_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"))
    