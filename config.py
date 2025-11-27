import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_PATH = "./lancedb_data"

# Tên bảng
TBL_PRODUCTS = "products"
TBL_IMAGES = "product_images"
TBL_KNOWLEDGE = "knowledge_base"

# Trọng số 
W_BRAND = 2.0
W_CATE  = 2.0
W_SPECS = 1.5
W_DESC  = 1.0