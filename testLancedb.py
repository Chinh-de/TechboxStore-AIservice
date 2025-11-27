import lancedb
import pandas as pd

# 1. Kết nối (Nó sẽ tự tạo thư mục data nếu chưa có)
db = lancedb.connect("./lancedb_data")

# 2. Tạo dữ liệu mẫu
data = pd.DataFrame({
    "vector": [[1.1, 1.2], [0.2, 1.8]],
    "item": ["Laptop", "Chuột"],
    "price": [20000, 500]
})

# 3. Tạo bảng
try:
    tbl = db.create_table("test_products", data, mode="overwrite")
    print(f"✅ Cài đặt thành công! Đã tạo bảng với {len(tbl)} dòng.")
except Exception as e:
    print(f"❌ Lỗi: {e}")