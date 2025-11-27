import os
import glob
import lancedb
from lancedb.pydantic import LanceModel, Vector
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm
import re

# --- CẤU HÌNH ---
DOCS_FOLDER = "./seedData/documents"       # Tạo folder này và ném file .md chính sách vào
DB_PATH = "../lancedb_data"   # Nơi lưu DB riêng cho RAG
TABLE_NAME = "knowledge_base"

def clean_markdown(text: str) -> str:
    """
    Loại bỏ các ký tự markdown cơ bản
    """
    text = text.strip()

    # Xóa heading markdown: #, ##, ###
    text = re.sub(r'^#+\s*', '', text)

    # Xóa bold, italic, code
    text = re.sub(r'(\*\*|\*|__|`)', '', text)

    # Xóa blockquote, list
    text = re.sub(r'^[-•>]\s*', '', text)

    return text.strip()

# --- 1. LOAD MODEL EMBEDDING ---
print(" Đang tải Model Embedding (dangvantuan)...")
model = SentenceTransformer('dangvantuan/vietnamese-document-embedding', trust_remote_code=True)
model.max_seq_length = 4096 
VECTOR_DIM = model.get_sentence_embedding_dimension()
print(f" Model OK. Dimension: {VECTOR_DIM}")

# --- 2. ĐỊNH NGHĨA SCHEMA LANCEDB ---
class KnowledgeChunk(LanceModel):
    source: str             # Tên nguồn
    text: str               # Nội dung đoạn văn
    vector: Vector(VECTOR_DIM) # Vector tương ứng

# --- 3. HÀM XỬ LÝ ---
def seed_data():
    # A. Đọc file
    files = glob.glob(os.path.join(DOCS_FOLDER, "*.*")) # Đọc tất cả file
    if not files:
        print(f" Lỗi: Không thấy file nào trong thư mục '{DOCS_FOLDER}'")
        return

    print(f" Tìm thấy {len(files)} tài liệu.")

    # B. Cấu hình bộ cắt (Vũ khí của LangChain)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,    # Kích thước đoạn (~200-300 từ)
        chunk_overlap=200,  # Gối đầu để không mất ngữ cảnh
        separators=["\n\n", "\n", "##", ".", ";", " ", ""]
    )

    data_to_insert = []

    # C. Vòng lặp xử lý
    for file_path in tqdm(files, desc="Xử lý file"):
        file_name = os.path.basename(file_path)  # fallback nếu không có title
        source_name = file_name
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f" Không đọc được file {file_name}: {e}")
            continue
        first_line = content.strip().splitlines()[0] if content.strip() else file_name
        source_name = clean_markdown(first_line) if first_line else file_name


        # Cắt nhỏ
        chunks = splitter.split_text(content)

        # Vector hóa từng đoạn
        for chunk in chunks:
            vec = model.encode([chunk])[0]
            
            data_to_insert.append({
                "source": source_name,
                "text": chunk,
                "vector": vec
            })

    # D. Lưu vào DB
    if data_to_insert:
        print(f" Đang lưu {len(data_to_insert)} chunks vào LanceDB...")
        db = lancedb.connect(DB_PATH)
        tbl = db.create_table(TABLE_NAME, schema=KnowledgeChunk, mode="overwrite")
        tbl.add(data_to_insert)
        print(f" HOÀN TẤT! Dữ liệu đã sẵn sàng tại '{DB_PATH}'")
    else:
        print(" Không có dữ liệu nào được tạo ra.")

if __name__ == "__main__":
    seed_data()