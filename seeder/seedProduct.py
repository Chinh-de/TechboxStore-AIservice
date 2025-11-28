import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np
import pickle
import os
from tqdm import tqdm

# --- 1. CẤU HÌNH ---
DB_PATH = "../lancedb_data"
TABLE_NAME = "products"

# Khai báo Schema cứng để đảm bảo dữ liệu chuẩn
# Lưu ý: Số chiều phải khớp với model bạn dùng (768 và 1920 như bài trước)
class ProductSchema(LanceModel):
    spu: str
    vector_search: Vector(768)   # Model dangvantuan (Semantic)
    vector_recs: Vector(1920)    # Hybrid (384*3 + 768)
    full_text: str               # Nội dung để RAG đọc

# --- 2. LOAD DỮ LIỆU ---
print(" Đang tải dữ liệu từ đĩa...")

try:
    # Load 2 file vector riêng biệt
    vecs_search = np.load('./seedData/vectors_search.npy')
    vecs_recs   = np.load('./seedData/vectors_recs.npy')
    
    with open('./seedData/product_spus.pkl', 'rb') as f:
        spus = pickle.load(f)
        
    with open('./seedData/product_full_detail.pkl', 'rb') as f:
        full_texts = pickle.load(f)

    print(f" Đã load:")
    print(f"   - {len(vecs_search)} Search Vectors (Dim: {vecs_search.shape[1]})")
    print(f"   - {len(vecs_recs)} Recs Vectors (Dim: {vecs_recs.shape[1]})")

except FileNotFoundError:
    print(" Lỗi: Không tìm thấy file .npy hoặc .pkl trong thư mục ./seedData/")
    exit()

# Kiểm tra tính toàn vẹn
if not (len(vecs_search) == len(vecs_recs) == len(spus)):
    print(" Lỗi: Số lượng dữ liệu không khớp nhau!")
    exit()

# --- 3. CHUẨN BỊ DATA LIST ---
print(" Đang map dữ liệu...")
data = []
for i in tqdm(range(len(spus))):
    data.append({
        "spu": str(spus[i]),
        "vector_search": vecs_search[i], # Nạp vào cột search
        "vector_recs": vecs_recs[i],     # Nạp vào cột recs
        "full_text": full_texts[i]
    })

# --- 4. LƯU VÀO LANCEDB ---
print(f" Đang ghi xuống LanceDB tại '{DB_PATH}'...")
db = lancedb.connect(DB_PATH)

# Tạo bảng với Schema định nghĩa sẵn (An toàn hơn để tự suy luận)
tbl = db.create_table(TABLE_NAME, schema=ProductSchema, mode="overwrite")
tbl.add(data)

print(f" HOÀN TẤT! Đã lưu {len(tbl)} sản phẩm.")
print(f"   - Table: {TABLE_NAME}")
print(f"   - Schema: {tbl.schema}")