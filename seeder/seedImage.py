import lancedb
import numpy as np
import pickle
import pandas as pd
import os

# --- CẤU HÌNH ---
PATH_FEATURES = './seedData/features.npy'
PATH_FILENAMES = './seedData/filenames.pkl'
DB_PATH = "../lancedb_data"
TABLE_NAME = "product_images"

# 1. LOAD DỮ LIỆU TỪ FILE
print("Đang tải dữ liệu từ file npy/pkl...")

if not os.path.exists(PATH_FEATURES) or not os.path.exists(PATH_FILENAMES):
    print("Lỗi: Không tìm thấy file dữ liệu đầu vào!")
    exit()

vectors = np.load(PATH_FEATURES)
with open(PATH_FILENAMES, 'rb') as f:
    filenames = pickle.load(f)

print(f"Đã load {len(vectors)} vector và {len(filenames)} tên file.")

# Kiểm tra khớp dữ liệu
if len(vectors) != len(filenames):
    print(f"Cảnh báo: Số lượng vector ({len(vectors)}) và tên file ({len(filenames)}) không khớp nhau!")
    exit()

# 2. CHUẨN BỊ DỮ LIỆU (TRÍCH XUẤT SKU)
print("Đang xử lý dữ liệu...")

data_list = []
for i, filename in enumerate(filenames):
    # Filename mẫu: "PRD-96394C6C-54E0-171b42f6.jpg" 
    
    # Trích xuất SKU: Lấy phần trước dấu gạch ngang thứ 2
    try:
        basename = filename.split('/')[-1]  # PRD-ABC-12345.jpg
        sku = "-".join(basename.split('-')[:2])
        
    except:
        sku = "UNKNOWN"

    data_list.append({
        "vector": vectors[i],      # LanceDB nhận trực tiếp numpy array
        "sku": sku,                # SKU để query ngược ra thông tin sản phẩm
    })

# 3. LƯU VÀO LANCEDB
print(f"Đang lưu vào LanceDB tại '{DB_PATH}'...")

# Kết nối DB
db = lancedb.connect(DB_PATH)

# Tạo bảng mới và nạp dữ liệu
tbl = db.create_table(TABLE_NAME, data_list)

print(f"HOÀN TẤT! Đã lưu {len(tbl)} dòng vào bảng '{TABLE_NAME}'.")
print("Schema của bảng:")
print(tbl.schema)