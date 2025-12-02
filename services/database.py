import lancedb
from lancedb.pydantic import LanceModel, Vector
from config import DB_PATH, TBL_PRODUCTS, TBL_IMAGES, TBL_KNOWLEDGE



class DatabaseManager:
    def __init__(self):
        self.db = None
        self.tables = {}

    def connect(self):
        print("🔌 Đang kết nối LanceDB...")
        self.db = lancedb.connect(DB_PATH)
        existing = self.db.table_names()
        
        # Helper để mở bảng an toàn
        def open_safe(name, key):
            if name in existing:
                self.tables[key] = self.db.open_table(name)
            else:
                print(f" Không tìm thấy bảng '{name}'")

        open_safe(TBL_PRODUCTS, 'products')
        open_safe(TBL_IMAGES, 'images')
        open_safe(TBL_KNOWLEDGE, 'knowledge_base')
      
            
        print(f" DB Connected: {list(self.tables.keys())}")

    def get_table(self, name):
        return self.tables.get(name)

db_manager = DatabaseManager()


class ProductSchema(LanceModel):
    spu: str
    vector_search: Vector(768)   # Model dangvantuan (Semantic)
    vector_recs: Vector(1920)    # Hybrid (384*3 + 768)
    full_text: str   

class ImageSchema(LanceModel):
    spu: str
    vector: Vector(2048)

class KnowledgeBaseSchema(LanceModel):
    id: int
    content: str
    vector: Vector(768)