from sentence_transformers import SentenceTransformer
from tensorflow.keras.applications.resnet50 import ResNet50
import google.generativeai as genai
from config import GOOGLE_API_KEY

class AIModelManager:
    def __init__(self):
        self.text_model = None
        self.image_model = None
        self.gemini_model = None

    def load_models(self):
        print(" Đang tải các Model AI...")
        
        # 1. Text Model
        self.text_model = SentenceTransformer('dangvantuan/vietnamese-document-embedding', trust_remote_code=True)
        self.text_model.max_seq_length = 4096
        
        # 2. Image Model
        self.image_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        
        # 3. Gemini
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
        else:
            print(" Thiếu API Key Gemini!")
            
        print(" Models đã sẵn sàng!")

# Singleton instance
ai_manager = AIModelManager()