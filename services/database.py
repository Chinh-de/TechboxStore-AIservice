import lancedb
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