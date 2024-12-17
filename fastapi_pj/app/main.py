import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from router import auth, todo, admin
import models
from database import engine

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="FastAPI with PostgreSQL and Minio",
    description="Combine PostgreSQL and Minio in one FastAPI app",
    openapi_url="/openapi.json",
    docs_url="/docs"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
models._database.Base.metadata.create_all(bind=engine)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
