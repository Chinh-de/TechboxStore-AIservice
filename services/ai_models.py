import os
from sentence_transformers import SentenceTransformer
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.models import load_model
import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL_NAME

class AIModelManager:
    def __init__(self):
        self.text_model = None
        self.image_model = None
        self.gemini_model = None
        self.short_text_model = None
        
        self.MODELS_DIR = "./models"
        
        if not os.path.exists(self.MODELS_DIR):
            os.makedirs(self.MODELS_DIR)

    def _get_sentence_transformer(self, online_name, local_folder_name):
        local_path = os.path.join(self.MODELS_DIR, local_folder_name)
        
        if os.path.exists(local_path):
            print(f"[Cached] Load từ: {local_path}")
            return SentenceTransformer(local_path, trust_remote_code=True)
        else:
            print(f"[Downloading] Đang tải {online_name}...")
            model = SentenceTransformer(online_name, trust_remote_code=True)
            model.save(local_path) # Lưu vào ./models/...
            print(f"Đã lưu model vào: {local_path}")
            return model

    def load_models(self):
        print(" Đang khởi động AI Model Manager...")
        
        # 1. Text Model (Vietnamese)
        try:
            self.text_model = self._get_sentence_transformer(
                online_name='dangvantuan/vietnamese-document-embedding',
                local_folder_name='vietnamese-document-embedding'
            )
        except Exception as e:
            print(f" Lỗi Text Model: {e}")

        # 2. Image Model (ResNet50)
        # ResNet lưu dạng file đơn (.h5) chứ không phải folder
        resnet_path = os.path.join(self.MODELS_DIR, 'resnet50_custom.h5')
        try:
            if os.path.exists(resnet_path):
                print(f"[Cached] Load ResNet từ: {resnet_path}")
                self.image_model = load_model(resnet_path)
            else:
                print("[Downloading] Đang tải ResNet50...")
                self.image_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
                self.image_model.save(resnet_path) # Lưu file .h5
                print(f"Đã lưu ResNet vào: {resnet_path}")
        except Exception as e:
            print(f"Lỗi Image Model: {e}")

        # 3. Short Text Model
        try:
            self.short_text_model = self._get_sentence_transformer(
                online_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
                local_folder_name='paraphrase-multilingual-MiniLM-L12-v2'
            )
        except Exception as e:
            print(f" Lỗi Short Text Model: {e}")

        # 4. Gemini (Online)
        if GOOGLE_API_KEY:
            try:
                genai.configure(api_key=GOOGLE_API_KEY)
                self.gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME or 'gemini-1.5-flash')
                print(" [Online] Gemini đã kết nối.")
            except Exception as e:
                print(f" Lỗi Gemini: {e}")
        else:
            print(" Thiếu API Key Gemini!")

        print(" Đã tải xong toàn bộ Models!")

# Singleton instance
ai_manager = AIModelManager()
# ai_manager.load_models() # Uncomment dòng này để chạy thử ngay