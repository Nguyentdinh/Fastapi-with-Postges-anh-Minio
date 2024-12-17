# dependencies.py

from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from models import User
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def require_admin(db: Session, token: str = Security(oauth2_scheme)):
    # Logic kiểm tra quyền admin
    user = db.query(User).filter(User.token == token).first()  # Điều chỉnh logic truy vấn
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privilege required")
    return user
