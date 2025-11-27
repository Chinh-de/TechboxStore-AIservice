import numpy as np
import io
from PIL import Image
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from services.ai_models import ai_manager

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: return v
    return v / norm

def encode_text(text):
    vec = ai_manager.text_model.encode([text])[0]
    # vec = normalize(vec) 
    return vec

def process_image_to_vector(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode != 'RGB': img = img.convert('RGB')
    img = img.resize((224, 224))
    
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    
    raw_vec = ai_manager.image_model.predict(x, verbose=0).flatten()
    return normalize(raw_vec)