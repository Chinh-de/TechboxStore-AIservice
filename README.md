# AI Super Service: Search - Recs - Chatbot

Ứng dụng FastAPI cung cấp các dịch vụ AI cho TechStore, bao gồm tìm kiếm sản phẩm, gợi ý cá nhân hóa và chatbot hỗ trợ khách hàng.

## Cài đặt

1. Cài đặt các thư viện phụ thuộc:
   ```
   pip install -r requirements.txt
   ```

2. Thiết lập biến môi trường:
   - Tạo file `.env` trong thư mục gốc và thêm:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     ```
   - Khóa API này cần thiết cho chức năng chatbot.

## Chạy ứng dụng

Chạy server với lệnh:
```
<!-- uvicorn main:app --reload -->
python server.py
```

API sẽ có sẵn tại `http://127.0.0.1:8000`

## Tài liệu API

### 1. Tìm kiếm sản phẩm bằng văn bản (`/search/text`)
- **Phương thức**: POST
- **Mô tả**: Tìm kiếm sản phẩm dựa trên truy vấn văn bản (semantic search).
- **Body** (JSON):
  ```json
  {
    "query": "Laptop gaming dưới 20 triệu",
    "top_k": 10
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "data": [
      {
        "sku": "DELL-G5-15",
        "score": 0.85
      }
    ]
  }
  ```

### 2. Gợi ý sản phẩm cá nhân hóa (`/recommend`)
- **Phương thức**: POST
- **Mô tả**: Gợi ý sản phẩm dựa trên lịch sử mua hàng của khách hàng.
- **Body** (JSON):
  ```json
  {
    "skus": ["DELL-G5-15", "HP-PAVILION"],
    "top_k": 5
  }
  ```
- **Response**:
  ```json
  {
    "data": [
      {
        "sku": "ASUS-ROG",
        "score": 0.92
      }
    ]
  }
  ```

### 3. Tìm kiếm sản phẩm bằng hình ảnh (`/search/image`)
- **Phương thức**: POST
- **Mô tả**: Upload hình ảnh để tìm kiếm sản phẩm tương tự.
- **Form Data**:
  - `file`: File hình ảnh (UploadFile)
  - `top_k`: Số lượng kết quả (int, mặc định 10)
- **Response**:
  ```json
  {
    "data": [
      {
        "sku": "DELL-G5-15",
        "score": 0.78
      }
    ]
  }
  ```

### 4. Chatbot hỗ trợ khách hàng (`/chat`)
- **Phương thức**: POST
- **Mô tả**: Chatbot sử dụng RAG để trả lời câu hỏi về sản phẩm và chính sách.
- **Body** (JSON):
  ```json
  {
    "question": "Laptop nào phù hợp cho gaming?",
    "history": [
      {
        "role": "user",
        "content": "Tôi cần mua laptop gaming."
      }
    ]
  }
  ```
- **Response**:
  ```json
  {
    "answer": "Dựa trên nhu cầu gaming của bạn, tôi khuyến nghị các mẫu laptop sau...",
    "intent": "PRODUCT",
    "related_products": ["DELL-G5-15", "ASUS-ROG"],
    "src": "policy_warranty.md",
    "debug_query": "Laptop gaming Dell dưới 20 triệu"
  }
  ```

## Tài liệu API tương tác
- Docs tương tác: `http://127.0.0.1:8000/docs`
- Docs thay thế: `http://127.0.0.1:8000/redoc`