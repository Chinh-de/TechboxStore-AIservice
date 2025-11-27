from fastapi import FastAPI, File, UploadFile, HTTPException
import numpy as np

# Import từ các module con
from schemas import SearchRequest, RecRequest, ChatRequest
from services.ai_models import ai_manager
from services.database import db_manager
from services.processing import process_image_to_vector, encode_text, normalize
from services.gemini_chat import route_question, generate_answer

app = FastAPI(title="AI Super Service (Modular)")

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
        out.append({"sku": r['sku'], "full_text": txt, "score": 1 - r['_distance']})
    return out

# --- API ENDPOINTS ---

@app.post("/search/text")
async def search_text(req: SearchRequest):
    res = search_products(req.query, k=req.top_k, return_full_text=False)
    return {"status": "success", "data": res}

@app.post("/recommend")
async def recommend(req: RecRequest):
    tbl = db_manager.get_table('products')
    if not tbl or not req.skus: return {"data": []}
    
    skus_str = ", ".join([f"'{s}'" for s in req.skus])
    items = tbl.search().where(f"sku IN ({skus_str})").limit(len(req.skus)).to_list()
    
    if not items: return {"data": []}
    
    # Logic Time Decay
    sku_to_vec = {item['sku']: np.array(item['vector_recs']) for item in items}
    ordered = [sku_to_vec[s] for s in req.skus if s in sku_to_vec]
    
    if not ordered: return {"data": []}
    
    weights = [0.9 ** i for i in range(len(ordered))]
    user_vec = np.average(ordered, axis=0, weights=weights)
    
    # Search
    results = tbl.search(user_vec, vector_column_name="vector_recs").metric("cosine").limit(req.top_k + len(req.skus)).to_list()
    
    final = []
    seen = set(req.skus)
    for r in results:
        if r['sku'] not in seen:
            final.append({"sku": r['sku'], "score": 1 - r['_distance']})
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
        if r['sku'] not in seen and r['sku'] != "UNKNOWN":
            final.append({"sku": r['sku'], "score": 1 - r['_distance']})
            seen.add(r['sku'])
        if len(final) >= top_k: break
    return {"data": final}

@app.post("/chat")
async def chat_bot(req: ChatRequest):
    if not ai_manager.gemini_model: raise HTTPException(503, "No Gemini Key")
    
    hist_str = "\n".join([f"{m.role}: {m.content}" for m in req.history[-6:]])
    
    # 1. Router
    router_res = route_question(req.question, hist_str)
    intent = router_res.get("intent", "CHITCHAT")
    query = router_res.get("optimized_query", req.question)
    
    ctx, instr, skus, src = "", "", [], ""
    
    # 2. Logic Intent
    if intent == "PRODUCT":
        found = search_products(query, k=5, return_full_text=True)
        if found:
            ctx = "[SẢN PHẨM]:\n" + "\n".join([f"- {p['full_text']}" for p in found])
            skus = [p['sku'] for p in found]
            instr = "Bạn là Sales. Tư vấn và mời mua."
        else:
            ctx = "Không tìm thấy sản phẩm."
            instr = "Xin lỗi và hỏi lại nhu cầu."
            
    elif intent == "POLICY":
        tbl = db_manager.get_table('knowledge')
        if tbl:
            vec = encode_text(query)
            res = tbl.search(vec).metric("cosine").limit(3).to_list()
            ctx = "[CHÍNH SÁCH]:\n" + "\n".join([f"- {r['text']}" for r in res])
            src = "\n".join([f"- {r.get('source','')}" for r in res])
        instr = "Bạn là CSKH. Trả lời theo chính sách."
        
    else:
        instr = "Bạn là trợ lý thân thiện. Chat vui vẻ."
        
    # 3. Generate
    ans = generate_answer(instr, ctx, hist_str, req.question)
    
    return {
        "answer": ans,
        "intent": intent,
        "related_products": skus,
        "src": src
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)