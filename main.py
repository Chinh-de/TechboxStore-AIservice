# import json
# import lancedb
# import numpy as np
# import io
# import os
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from pydantic import BaseModel
# from typing import List, Optional
# from PIL import Image

# # --- IMPORT MODELS ---
# from sentence_transformers import SentenceTransformer
# from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
# from tensorflow.keras.preprocessing import image
# import google.generativeai as genai

# from dotenv import load_dotenv
# load_dotenv()


# app = FastAPI(title="AI Super Service: Search - Recs - Chatbot")

# # --- CẤU HÌNH CHUNG ---
# DB_PATH = "./lancedb_data"
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Đảm bảo đã set biến môi trường hoặc thay trực tiếp
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# # config weight
# W_BRAND = 2.0  # Ưu tiên Hãng
# W_CATE  = 2.0  # Ưu tiên Loại
# W_SPECS = 1.5  # Ưu tiên Cấu hình
# W_DESC = 1.0

# # Tên các bảng trong LanceDB
# TBL_PRODUCTS = "products"        # Chứa vector Search & Recs
# TBL_IMAGES = "product_images"    # Chứa vector Ảnh
# TBL_KNOWLEDGE = "knowledge_base"       # Chứa tài liệu RAG (Lưu ý: Tên bảng phải khớp với file seed_rag.py)

# # Biến toàn cục (Singleton)
# models = {}
# db_tables = {}

# # --- HÀM TIỆN ÍCH ---
# # def normalize(v):
# #     norm = np.linalg.norm(v)
# #     if norm == 0: return v
# #     return v / norm

# def process_image_to_vector(img_bytes):
#     img = Image.open(io.BytesIO(img_bytes))
#     if img.mode != 'RGB': img = img.convert('RGB')
#     img = img.resize((224, 224))
#     img_array  = image.img_to_array(img)
#     expanded_img_array = np.expand_dims(img_array, axis=0)
#     preprocessed_img = preprocess_input(expanded_img_array)
#     features  = models['image'].predict(preprocessed_img, verbose=0).flatten()
#     return features

# # --- KHỞI TẠO SERVER (CHẠY 1 LẦN) ---
# @app.on_event("startup")
# async def startup_event():
#     print(" Đang khởi động AI Super Service...")
    
#     # 1. Load Text Model (Dùng chung cho cả Search và Chatbot)
#     print("   - Loading Text Model (dangvantuan)...")
#     models['text'] = SentenceTransformer('dangvantuan/vietnamese-document-embedding', trust_remote_code=True)
#     models['text'].max_seq_length = 4096
    
#     # 2. Load Image Model (ResNet50)
#     print("   - Loading Image Model (ResNet50)...")
#     models['image'] = ResNet50(weights='imagenet', include_top=False, pooling='avg')
    
#     # 3. Setup Gemini
#     print("   - Configuring Gemini...")
#     if GOOGLE_API_KEY:
#         genai.configure(api_key=GOOGLE_API_KEY)
#         models['gemini'] = genai.GenerativeModel('gemini-2.0-flash-lite')
#     else:
#         print(" Chưa có GOOGLE_API_KEY. Chatbot sẽ không hoạt động.")

#     # 4. Kết nối LanceDB
#     print("   - Connecting Database...")
#     db = lancedb.connect(DB_PATH)
#     existing_tables = db.table_names()
    
#     # Mở bảng Products
#     if TBL_PRODUCTS in existing_tables:
#         db_tables['products'] = db.open_table(TBL_PRODUCTS)
#     else:
#         print(f" Thiếu bảng '{TBL_PRODUCTS}'. API Search/Recs sẽ lỗi.")

#     # Mở bảng Images
#     if TBL_IMAGES in existing_tables:
#         db_tables['images'] = db.open_table(TBL_IMAGES)
#     else:
#         print(f" Thiếu bảng '{TBL_IMAGES}'. API Search Image sẽ lỗi.")

#     # Mở bảng Knowledge (Cho Chatbot)
#     if TBL_KNOWLEDGE in existing_tables:
#         db_tables['knowledge'] = db.open_table(TBL_KNOWLEDGE)
#     else:
#         if "knowledge_base" in existing_tables:
#              db_tables['knowledge'] = db.open_table("knowledge_base")
#         else:
#              print(f" Thiếu bảng '{TBL_KNOWLEDGE}'. Chatbot sẽ lỗi.")

#     print(" Hệ thống đã sẵn sàng!")

# # --- DTOs ---
# class ChatMessage(BaseModel):
#     role: str
#     content: str

# class ChatRequest(BaseModel):
#     question: str
#     history: List[ChatMessage] = []

# class SearchRequest(BaseModel):
#     query: str
#     top_k: int = 10

# class RecRequest(BaseModel):
#     spus: List[str]
#     top_k: int = 10
# def route_question(user_query, history_text):
#     """
#     Dùng Gemini để phân loại câu hỏi và tối ưu hóa query.
#     Trả về JSON: { "intent": "PRODUCT"|"POLICY"|"CHITCHAT", "optimized_query": "..." }
#     """
#     prompt = f"""
#     Bạn là bộ não phân loại tin nhắn cho TechStore.
    
#     LỊCH SỬ CHAT:
#     {history_text}
    
#     CÂU KHÁCH HỎI: "{user_query}"
    
#     NHIỆM VỤ:
#     1. Phân loại ý định (intent) vào 1 trong 3 nhóm:
#        - POLICY: Hỏi về các chủ đề: Khách Hàng Doanh Nghiệp & Dự Án, Chính Sách Khách Hàng, Chính Sách Thanh Toán & Vận Chuyển, Thu Cũ Đổi Mới, Bảo Hành & Đổi Trả, Bảo Mật Thông Tin, Vệ Sinh & Nâng Cấp Thiết Bị, Điều Khoản Dịch Vụ, Hướng Dẫn Khắc Phục Sự Cố Cơ Bản, Giới Thiệu Về Techbox Store.
#        - PRODUCT: Hỏi mua, tư vấn, so sánh, mô tả nhu cầu, tìm sản phẩm (laptop, chuột, phím...).
#        - CHITCHAT: Chào hỏi, cảm ơn, trêu đùa, hoặc không liên quan mua bán.
       
#     2. Viết lại câu hỏi (optimized_query) để tìm kiếm tốt hơn:
#        - Nếu là PRODUCT: Tóm tắt nhu cầu thành keywords (VD: "Máy rẻ" -> "Laptop giá rẻ dưới 10 triệu").
#        - Nếu là POLICY: Viết rõ ràng (VD: "Bảo hành ko?" -> "Chính sách bảo hành").
#        - Nếu là CHITCHAT: Giữ nguyên.
       
#     OUTPUT JSON FORMAT:
#     {{
#         "intent": "PRODUCT", 
#         "optimized_query": "Laptop gaming Dell dưới 20 triệu"
#     }}
#     Chỉ trả về JSON thuần, không markdown.
#     """
    
#     try:
#         response = models['gemini'].generate_content(prompt)
#         text = response.text.strip().replace('```json', '').replace('```', '')
#         return json.loads(text)
#     except:
#         # Fallback nếu lỗi JSON
#         return {"intent": "CHITCHAT", "optimized_query": user_query}




# def search_products(query: str, k: int =10, return_full_text: bool = True):
#     """
#     Tìm kiếm sản phẩm và trả về danh sách chi tiết.
#     Output format: List[{'spu': str, 'full_text': str, 'score': float}]
#     """
#     if 'products' not in db_tables: 
#         return []
    
#     # Encode & Normalize
#     query_vec = models['text'].encode([query])[0]
#     # query_vec = normalize(query_vec)
    
#     # Search LanceDB
#     results = db_tables['products'].search(query_vec, vector_column_name="vector_search") \
#         .metric("cosine").limit(k).to_list()
        
#     structured_results = []
#     text_content = ""
#     for r in results:
#         # Lấy thông tin text để Gemini đọc
#         if return_full_text:
#             text_content = r.get('full_text', '')
        
#         structured_results.append({
#             "spu": r['spu'],          # SPU để trả về Frontend
#             "full_text": text_content, # Text để đưa vào Prompt
#             "score": 1 - r['_distance'] # Độ giống
#         })
    
#     return structured_results

# # ==========================================
# # API 1: TÌM KIẾM TEXT (Semantic Search)
# # ==========================================

# @app.post("/search/text")
# async def search_text(req: SearchRequest):
#     try:
#         results = search_products(
#             query=req.query, 
#             k=req.top_k, 
#             return_full_text=False 
#         )
        
#         return {"status": "success", "data": results}
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # ==========================================
# # API 2: GỢI Ý (Personalized Recommendation)
# # ==========================================
# @app.post("/recommend")
# async def recommend(req: RecRequest):
#     try:
#         if not req.spus: return {"data": []}

#         # 1. Lấy dữ liệu từ DB
#         # fixbug: LanceDB trả về thứ tự ngẫu nhiên
#         spus_str = ", ".join([f"'{s}'" for s in req.spus])
#         items = db_tables['products'].search().where(f"spu IN ({spus_str})").limit(len(req.spus)).to_list()
        
#         if not items: return {"data": []}

#         # 2. Map spu -> Vector để đồng bộ thứ tự
#         # Giả sử req.spus gửi lên theo thứ tự: [Cũ nhất, ..., Mới nhất]
#         spu_to_vec = {item['spu']: np.array(item['vector_recs']) for item in items}
        
#         ordered_vectors = []
#         found_spus = [] 
        
#         for spu in req.spus:
#             if spu in spu_to_vec:
#                 ordered_vectors.append(spu_to_vec[spu])
#                 found_spus.append(spu)
        
#         if not ordered_vectors: return {"data": []}

#         # 3. Tính Vector Trung Bình với Trọng số Thời gian (Time Decay)
#         DECAY_FACTOR = 0.9
#         n = len(ordered_vectors)
        
#         # Tạo mảng trọng số: 
#         # i chạy từ 0 -> n-1. 
#         # i=0 (Mới nhất) -> 0.9^0 = 1.0
#         # i=1 (Cũ hơn)   -> 0.9^1 = 0.9
#         weights = [DECAY_FACTOR ** i for i in range(n)]
        
#         # Tính trung bình có trọng số
#         user_vec = np.average(ordered_vectors, axis=0, weights=weights)
        
#         # 4. Chuẩn hóa vector User
#         # user_vec = normalize(user_vec)
        
#         # 5. Tìm kiếm
#         # Lấy dư ra (top_k + số lượng lịch sử) để trừ hao
#         results = db_tables['products'].search(user_vec, vector_column_name="vector_recs") \
#             .metric("cosine") \
#             .limit(req.top_k + len(found_spus)) \
#             .to_list()
            
#         # 6. Lọc bỏ sản phẩm đã có
#         final = []
#         seen = set(found_spus)
        
#         for r in results:
#             if r['spu'] not in seen:
#                 final.append({
#                     "spu": r['spu'], 
#                     "score": 1 - r['_distance']
#                 })
#                 if len(final) >= req.top_k: break
                
#         return {"data": final}
        
#     except Exception as e:
#         print(f"Error Recommend: {e}")
#         raise HTTPException(500, str(e))

# # ==========================================
# # API 3: TÌM KIẾM ẢNH (Image Search)
# # ==========================================
# @app.post("/search/image")
# async def search_image(file: UploadFile = File(...), top_k: int = 10):
#     try:
#         content = await file.read()
#         vec = process_image_to_vector(content)
        
#         results = db_tables['images'].search(vec).metric("cosine").limit(top_k*3).to_list()
        
#         final = []
#         seen = set()
#         for r in results:
#             if r['spu'] not in seen and r['spu'] != "UNKNOWN":
#                 final.append({"spu": r['spu'], "score": 1 - r['_distance']})
#                 seen.add(r['spu'])
#             if len(final) >= top_k: break
#         return {"data": final}
#     except Exception as e:
#         raise HTTPException(500, str(e))

# # ==========================================
# # API 4: CHATBOT RAG (Gemini + LanceDB)
# # ==========================================
# @app.post("/chat")
# async def chat_bot(req: ChatRequest):
#     if 'gemini' not in models: raise HTTPException(503, "Gemini not configured")
    
#     try:
#         # 1. Chuẩn bị lịch sử
#         hist_str = "\n".join([f"{m.role}: {m.content}" for m in req.history[-6:]])
        
#         # 2. GỌI ROUTER (Phân loại ý định)
#         router_res = route_question(req.question, hist_str)
#         intent = router_res.get("intent", "CHITCHAT")
#         search_query = router_res.get("optimized_query", req.question)
        
#         print(f"🔍 Intent: {intent} | Query: {search_query}")
        
#         context_str = ""
#         system_instruction = ""
        
#         suggested_spus = []
#         src = ""
        
#         # 3. XỬ LÝ THEO NHÁNH
#         if intent == "PRODUCT":
#             products_found = search_products(search_query, k=5)
            
#             if products_found:
#                 # A. Tạo Context cho Gemini (Lấy full_text)
#                 # Thêm số thứ tự để Gemini dễ trích dẫn
#                 prod_texts = [f"{i+1}. {p['full_text']}" for i, p in enumerate(products_found)]
#                 context_str = f"[DANH SÁCH SẢN PHẨM PHÙ HỢP]:\n" + "\n".join(prod_texts)
                
#                 # B. Lấy spu để trả về Frontend (Lấy spu)
#                 suggested_spus = [p['spu'] for p in products_found]
                
#                 system_instruction = "Bạn là nhân viên Sales. Dựa vào danh sách sản phẩm trên để tư vấn, so sánh và mời khách mua các sản phẩm đi kèm."
#             else:
#                 context_str = "Không tìm thấy sản phẩm nào khớp với yêu cầu."
#                 system_instruction = "Xin lỗi khách và hỏi thêm nhu cầu chi tiết hơn."
            
#         elif intent == "POLICY":
#             if 'knowledge' in db_tables:
#                 # q_vec = normalize(models['text'].encode([search_query])[0])
#                 q_vec = models['text'].encode([search_query])[0]
#                 res = db_tables['knowledge'].search(q_vec).metric("cosine").limit(5).to_list()

#                 src = "\n".join([f"- {r['source']}" for r in res])

#                 policy_text = "\n".join([f"- {r['text']}" for r in res])
#                 context_str = f"[THÔNG TIN CHÍNH SÁCH]:\n{policy_text}"
#             system_instruction = "Bạn là nhân viên CSKH. Trả lời thắc mắc dựa trên chính sách. Nếu không có thông tin, hãy bảo khách gọi hotline 1900 1234."
            
#         else: # CHITCHAT
#             system_instruction = "Bạn là trợ lý ảo TechStore thân thiện. Hãy trò chuyện vui vẻ nhưng khéo léo lái về chủ đề công nghệ."

        
#         # 4. TẠO PROMPT
#         final_prompt = f"""
#         {system_instruction}

#         Định dạng trả về: Chỉ trả lời văn bản thuần, không markdown.
        
#         DỮ LIỆU THAM KHẢO:
#         {context_str}
        
#         LỊCH SỬ CHAT:
#         {hist_str}
        
#         KHÁCH HỎI: "{req.question}"
#         TRẢ LỜI:
#         """
        
#         # 5. GENERATE
#         response = models['gemini'].generate_content(final_prompt)
        
#         # 6. TRẢ VỀ KẾT QUẢ (KÈM spu)
#         return {
#             "answer": response.text.strip(),
#             "intent": intent,
#             "related_products": suggested_spus,
#             "src" : src,
#             "debug_query": search_query
#         }

#     except Exception as e:
#         print(f"Error: {e}")
#         return {"answer": "Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau.", "intent": "ERROR", "related_products": []}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)