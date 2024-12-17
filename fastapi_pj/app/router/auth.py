from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from models import User
from passlib.context import CryptContext
import database as _database
import sqlalchemy.orm as _orm
from datetime import timedelta, datetime
from jose import jwt, JWTError

# Router Configuration
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Secret Key and Algorithm for JWT
SECRET_KEY = "d75139333e27218e99bb150b0c7003b67ad1e708ab4651942c4f5686182c1947"  
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Models for Requests and Responses
class CreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    user_name: str
    hashed_password: str
    email: str
    role: str  # Ensure role is provided when creating a user

class Token(BaseModel):
    access_token: str
    token_type: str

# Dependency for Database
def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication Helpers
def authenticate_user(username: str, password: str, db: _orm.Session):
    user = db.query(User).filter(User.user_name == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None or user_role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        print(f"Decoded Token - Username: {username}, Role: {user_role}")  # Debugging info
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError as e:
        print(f"JWT Error: {e}")  # Debugging info
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        
def admin_required(user: dict = Depends(get_current_user)):
    if user['role'] != 'admin':  # Kiểm tra nếu không phải admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return user

@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(
    create_user_request: CreateUserRequest,
    user: dict = Depends(admin_required),
    db: _orm.Session = Depends(get_db)
):
    # Check if username already exists
    existing_user = db.query(User).filter(User.user_name == create_user_request.user_name).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )
    # Hash password and create user
    create_user_model = User(
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        user_name=create_user_request.user_name,
        hashed_password=bcrypt_context.hash(create_user_request.hashed_password),
        is_active=True,
        email=create_user_request.email,
        role=create_user_request.role
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: _orm.Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user."
        )
    print(f"User Role: {user.role}")  # Debugging info
    token = create_access_token(user.user_name, user.id, user.role, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
