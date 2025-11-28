from fastapi import FastAPI, File, UploadFile, HTTPException
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

# Import từ các module con
from schemas import SearchRequest, RecRequest, ChatRequest
from services.ai_models import ai_manager
from services.database import db_manager
from services.processing import process_image_to_vector, encode_text, normalize
from services.gemini_chat import route_question, generate_answer
from config import SIMILARITY_THRESHOLD_PRODUCT, SIMILARITY_THRESHOLD_POLICY

app = FastAPI(title="AI Service for TechBoxStore")

@app.on_event("startup")
async def startup_event():
    ai_manager.load_models()
    db_manager.connect()

# --- HELPER SEARCH ---
def search_products(query, k=10, return_full_text=True):
    tbl = db_manager.get_table('products')
    if not tbl: return []
    
    vec = encode_text(query)
    results = tbl.search(vec, vector_column_name="vector_search").metric("cosine").limit(k).to_list()
    
    out = []
    for r in results:
        txt = r.get('full_text') if return_full_text else ""
        out.append({"spu": r['spu'], "full_text": txt, "score": 1 - r['_distance']})
    return out

# --- API ENDPOINTS ---

@app.post("/search/text")
async def search_text(req: SearchRequest):
    res = search_products(req.query, k=req.top_k, return_full_text=False)
    return {"status": "success", "data": res}

@app.post("/recommend")
async def recommend(req: RecRequest):
    tbl = db_manager.get_table('products')
    if not tbl or not req.spus: return {"data": []}
    
    spus_str = ", ".join([f"'{s}'" for s in req.spus])
    items = tbl.search().where(f"spu IN ({spus_str})").limit(len(req.spus)).to_list()
    
    if not items: return {"data": []}
    
    # Logic Time Decay
    spu_to_vec = {item['spu']: np.array(item['vector_recs']) for item in items}
    ordered = [spu_to_vec[s] for s in req.spus if s in spu_to_vec]
    
    if not ordered: return {"data": []}
    
    weights = [0.9 ** i for i in range(len(ordered))]
    user_vec = np.average(ordered, axis=0, weights=weights)
    
    # Search
    results = tbl.search(user_vec, vector_column_name="vector_recs").metric("cosine").limit(req.top_k + len(req.spus)).to_list()
    
    final = []
    seen = set(req.spus)
    for r in results:
        if r['spu'] not in seen:
            final.append({"spu": r['spu'], "score": 1 - r['_distance']})
            if len(final) >= req.top_k: break
            
    return {"data": final}

@app.post("/search/image")
async def search_image(file: UploadFile = File(...), top_k: int = 10):
    tbl = db_manager.get_table('images')
    if not tbl: return {"data": []}
    
    content = await file.read()
    vec = process_image_to_vector(content)
    
    results = tbl.search(vec).metric("cosine").limit(top_k*3).to_list()
    
    final = []
    seen = set()
    for r in results:
        if r['spu'] not in seen and r['spu'] != "UNKNOWN":
            final.append({"spu": r['spu'], "score": 1 - r['_distance']})
            seen.add(r['spu'])
        if len(final) >= top_k: break
    return {"data": final}

@app.post("/chat")
async def chat_bot(req: ChatRequest):
    if not ai_manager.gemini_model: raise HTTPException(503, "No Gemini Key")
    
    hist_str = "\n".join([f"{m.role}: {m.content}" for m in req.history[-6:]])
    
    # 1. Router
    print(f"Routing question: {req.question}")
    router_res = route_question(req.question, hist_str)
    intent = router_res.get("intent", "CHITCHAT")
    print(f"Intent: {intent}")
    query = router_res.get("optimized_query", req.question)
    print(f"Optimized Query: {query}")
    
    ctx, instr, spus, src = "", "", [], ""
    
    # 2. Logic Intent
    if intent == "PRODUCT":
        search_results = search_products(query, k=5, return_full_text=True)
        found = [p for p in search_results if p['score'] >= SIMILARITY_THRESHOLD_PRODUCT]
        if found:
            ctx = "[SẢN PHẨM]:\n" + "\n".join([f"- {p['full_text']}" for p in found])
            spus = [p['spu'] for p in found]
            instr = """
            VAI TRÒ: Bạn là Chuyên viên tư vấn công nghệ tại TechBoxStore.
            MỤC TIÊU: Giúp khách hàng chọn được sản phẩm phù hợp nhất trong danh sách và chốt đơn.
            
            YÊU CẦU TRẢ LỜI:
            1. Dựa CHẶT CHẼ vào 'DANH SÁCH SẢN PHẨM TÌM THẤY' bên trên.
            2. Nếu có nhiều sản phẩm, hãy so sánh ngắn gọn ưu/nhược điểm (VD: Con này mạnh hơn về đồ họa, con kia pin trâu hơn).
            3. Luôn đưa ra mức giá để khách cân nhắc.
            4. Giọng văn: Nhiệt tình, chuyên nghiệp, dùng emoji vừa phải.
            5. Tuyệt đối không bịa đặt tính năng không có trong dữ liệu.
            """
        else:
            ctx = "Không tìm thấy sản phẩm nào khớp với yêu cầu."
            instr = """
            VAI TRÒ: Chuyên viên tư vấn.
            TÌNH HUỐNG: Khách hỏi sản phẩm mà cửa hàng hiện không có hoặc mô tả chưa rõ.
            HÀNH ĐỘNG:
            1. Khéo léo xin lỗi vì chưa tìm thấy sản phẩm chính xác.
            2. Gợi ý khách cung cấp thêm chi tiết (Tầm tiền, hãng yêu thích, nhu cầu cụ thể hơn).
            3. Đừng bịa ra sản phẩm.
            4. Không đề cập đến giá vì sẽ hiện thị giá ngay bên dưới.
            """
            
    elif intent == "POLICY":
        tbl = db_manager.get_table('knowledge_base')
        if tbl:
            vec = encode_text(query)
            chunks = tbl.search(vec).metric("cosine").limit(5).to_list()
            res = [r for r in chunks if (1 - r['_distance']) >= SIMILARITY_THRESHOLD_POLICY]
            ctx = "[THÔNG TIN CÓ THỂ LIÊN QUAN]:\n" + "\n".join([f"- {r['text']}" for r in res])
            src = "\n".join([f"- {r.get('source','')}" for r in res])
        instr = """
                VAI TRÒ: Nhân viên Chăm sóc khách hàng (CSKH) tận tâm.
                MỤC TIÊU: Giải đáp thắc mắc về quy định, bảo hành, đổi trả.
                
                YÊU CẦU TRẢ LỜI:
                1. Trả lời chính xác dựa trên thông tin đi kèm. Không chém gió.
                2. Nếu thông tin không đủ để trả lời, hãy hướng dẫn khách gọi hotline 19001234.
                3. Giọng văn: Lịch sự, đồng cảm (nếu khách khiếu nại), rõ ràng.
                """
        
    else:
        ctx = "Không có dữ liệu tra cứu."
        instr = """
        VAI TRÒ: Trợ lý ảo thân thiện của TechBoxStore.
        HÀNH ĐỘNG: 
        - Trò chuyện vui vẻ, ngắn gọn với khách.
        - Nếu khách hỏi ngoài lề (thời tiết, bóng đá...), hãy khéo léo lái về công nghệ hoặc sản phẩm của shop.
        - Luôn giữ thái độ phục vụ.
        """
        
    # 3. Generate

    print("="*20)
    print("Generating answer...")
    print(f"System Instruction: {instr}")
    print(f"Context: {ctx}")
    print(f"History: {hist_str}")
    print(*"="*20)
    

    ans = generate_answer(instr, ctx, hist_str, req.question)
    print(f"Answer from Gemini: {ans}")
    
    return {
        "answer": ans,
        "intent": intent,
        "related_products": spus,
        "src": src
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)