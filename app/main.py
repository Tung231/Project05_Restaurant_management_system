from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Thêm thư viện xử lý file tĩnh (ảnh, css, js)

# Import các router API
from app.routers import customer, menu, reservation, invoice
# Import Router Web (Giao diện HTML)
from app.routers import web_ui 
from app.routers import table

# 1. Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Restaurant Management System API",
    description="Hệ thống quản lý nhà hàng - Đồ án SQL & Python (DATCOM Lab - NEU)",
    version="1.0.0",
    docs_url="/docs",      # Đường dẫn trang Swagger UI để test API
    redoc_url="/redoc"
)

# 2. Cấu hình thư mục chứa file tĩnh
# LƯU Ý: FastAPI yêu cầu phải có sẵn thư mục này. Hãy tạo một thư mục rỗng tên 'static' nằm trong thư mục 'app'.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 3. Cấu hình CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Đăng ký Router giao diện Web
# Router này sẽ tiếp quản đường dẫn gốc "/" và hiển thị file index.html
app.include_router(web_ui.router)

@app.get("/ping", tags=["Test"])
def test_ping():
    return {"message": "Server vẫn sống nhăn răng!"}

# 5. Đăng ký các Router API 
app.include_router(customer.router)
app.include_router(menu.router)
app.include_router(reservation.router)
app.include_router(invoice.router)
app.include_router(table.router)

# Cách chạy Server (Sử dụng lệnh trong Terminal):
# uvicorn app.main:app --reload