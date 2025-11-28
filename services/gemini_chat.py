import json
from services.ai_models import ai_manager

def route_question(user_query, history_text):
    prompt = f"""
    Bạn là bộ não phân loại tin nhắn cho TechStore.
    LỊCH SỬ CHAT: {history_text}
    CÂU KHÁCH HỎI: "{user_query}"
    
    NHIỆM VỤ:
    1. Phân loại ý định (intent) vào 1 trong 3 nhóm:
        - POLICY: Hỏi về các chủ đề: Khách Hàng Doanh Nghiệp & Dự Án, Chính Sách Khách Hàng, Chính Sách Thanh Toán & Vận Chuyển, Thu Cũ Đổi Mới, Bảo Hành & Đổi Trả, Bảo Mật Thông Tin, Vệ Sinh & Nâng Cấp Thiết Bị, Điều Khoản Dịch Vụ, Hướng Dẫn Khắc Phục Sự Cố Cơ Bản, Giới Thiệu Về Techbox Store.
        - PRODUCT: Hỏi mua, tư vấn, so sánh, mô tả nhu cầu, tìm sản phẩm (laptop, chuột, phím...).
        - CHITCHAT: Chào hỏi, cảm ơn, trêu đùa, hoặc không liên quan mua bán.
        
    2. Viết lại câu hỏi (optimized_query) để tìm kiếm tốt hơn:
        - Dựa vào lịch sử chat để hiểu rõ câu hỏi.
        - Nếu khách dùng đại từ ("nó", "máy đó", "cái này"), hãy thay thế bằng tên sản phẩm cụ thể đã nhắc trước đó.
        - Nếu là PRODUCT: Loại bỏ các chi tiết gây nhiễu, thêm các đặc điểm kỹ thuật, từ đồng nghĩa nếu có thể, giữ nguyên tên model/hãng.
        - Nếu là POLICY: Viết rõ ràng, đừng viết chung chung. Hãy viết thành câu hỏi cụ thể chứa từ khóa chính sách
        - Nếu là CHITCHAT: Giữ nguyên.
       
    OUTPUT JSON FORMAT:
    {{
        "intent": "PRODUCT", 
        "optimized_query": "Laptop gaming Dell cấu hình cao"
    }}
    Chỉ trả về JSON thuần, không markdown.
    """
    try:
        response = ai_manager.gemini_model.generate_content(prompt)
        text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(text)
    except:
        return {"intent": "CHITCHAT", "optimized_query": user_query}

def generate_answer(system_instruction, context_str, hist_str, question):
    prompt = f"""
    {system_instruction}
    Định dạng trả về: Chỉ trả lời văn bản thuần, không markdown.
    
    DỮ LIỆU ĐÃ THAM KHẢO:
    {context_str}
    
    LỊCH SỬ CHAT:
    {hist_str}
    
    KHÁCH HỎI: "{question}"
    TRẢ LỜI:
    """
    response = ai_manager.gemini_model.generate_content(prompt)
    return response.text.strip()