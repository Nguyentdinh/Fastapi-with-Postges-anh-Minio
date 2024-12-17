# Sử dụng image Python chính thức làm base
FROM python:3.11

# Đặt thư mục làm việc bên trong container
WORKDIR /app

# Copy file requirements.txt vào container
COPY requirement.txt .

# Cài đặt các thư viện từ requirements.txt
RUN pip install --no-cache-dir -r requirement.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose port 8000 để FastAPI có thể truy cập
EXPOSE 8000

# Chạy FastAPI bằng Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
