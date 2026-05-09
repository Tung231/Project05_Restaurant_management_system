import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

# 1. Tải cấu hình từ file .env
load_dotenv()

# 2. Khởi tạo Hồ chứa kết nối (Connection Pool)
# Chúng ta sẽ chốt tên biến là: db_pool
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="restaurant_pool",
        pool_size=10, # Cho phép tối đa 10 người truy cập web cùng lúc
        pool_reset_session=True,
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "RestaurantManagement"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "")
    )
    print("✅ [Cơ sở dữ liệu]: Đã khởi tạo Connection Pool thành công!")
except mysql.connector.Error as err:
    print(f"❌ [Lỗi CSDL]: Không thể khởi tạo Pool - {err}")
    db_pool = None

# 3. Hàm cấp phát kết nối cho Web và API
def get_db():
    if db_pool is None:
        raise Exception("Hệ thống chưa kết nối được MySQL. Hãy kiểm tra lại file .env!")
        
    # Gọi đúng cái tên db_pool đã tạo ở trên
    db = db_pool.get_connection() 
    try:
        yield db
    finally:
        db.close() # Nhiệm vụ tối thượng: Phục vụ web xong phải trả kết nối về Pool!