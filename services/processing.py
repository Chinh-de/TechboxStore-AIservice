import numpy as np
import io
import re
import requests
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

def encode_short_text(text):
    vec = ai_manager.short_text_model.encode([text])[0]
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

def encode_image_from_url(img_url):
    response = requests.get(img_url)
    if response.status_code == 200:
        img_bytes = response.content
        return process_image_to_vector(img_bytes)
    else:
        raise ValueError(f"Failed to fetch image from URL: {img_url}")
    
def clean_md(description: str) -> str:
    if not description:
        return ""

    # Bỏ ảnh markdown ![alt](url)
    description = re.sub(r'!\[.*?\]\(.*?\)', '', description)

    # Bỏ link markdown [text](url)
    description = re.sub(r'\[.*?\]\(.*?\)', '', description)

    # Thay | bằng khoảng trắng
    description = description.replace('|', ' ')

    # Thay các ký tự đặc biệt #, *, > bằng khoảng trắng
    description = re.sub(r'[#*>]', ' ', description)

    # Xóa khoảng trắng thừa
    description = re.sub(r'\s+', ' ', description).strip()

    return description


def create_product_embedding_data(product):
    # thông tin sản phẩm
    spu = product.get('spu', '')
    name = product.get('name', '')
    categoryName = product.get('categoryName', '')
    brandName = product.get('brandName', '')
    description = product.get('description', '')
    
    attributes = product.get('attributes', [])
    common_specs_list = []
    for attr in attributes:
        attr_name = attr.get('name', '')
        attr_val = attr.get('value', '')
        if attr_name and attr_val:
            common_specs_list.append(f"{attr_name} {attr_val}")
    common_specs_str = ", ".join(common_specs_list)
    
    variants_list = product.get('variations') or product.get('variants') or []
    variant_texts = []
    image_list = []

    main_image = product.get('imageUrl')
    if main_image:
        image_list.append(main_image)


    for v in variants_list:
        variant_name = v.get('variationName', '')
        variant_attributes = v.get('attributes', [])
        variant_attributes_list = []

        if isinstance(variant_attributes, list):
            for attr in variant_attributes:
                a_name = attr.get('name', '')
                a_val = attr.get('value', '')
                variant_attributes_list.append(f"{a_name} {a_val}")

            variant_attributes_str = ", ".join(variant_attributes_list)
            variant_texts.append(f"Phiên bản {variant_name} với các thuộc tính {variant_attributes_str}")
        
        v_images = v.get('images', [])
        for img_obj in v_images:
            img_url = img_obj.get('imageUrl')
            if img_url:
                image_list.append(img_url)
    
    variants_str = ". ".join(list(set(variant_texts)))

    # xử lí lọc md ở mô tả
    description = clean_md(description)
    

    #  tạo dữ liệu search
    full_text_search = (
        f"Sản phẩm: {name}. "
        f"Thương hiệu: {brandName}. "
        f"Danh mục: {categoryName}. "
        f"Cấu hình chung: {common_specs_str}. "
        f"Các tùy chọn biến thể: {variants_str}. " 
        f"Mô tả chi tiết: {description}"                
    ).lower()

    # trả về các phần riêng biệt để cho recommendation
    specs_combined = f"{common_specs_str}. {variants_str}".lower()
    desc_have_name = f"Sản phẩm: {name} . Mô tả: {description}"

    return {
        "search_text": full_text_search, 
        "parts": {                       
            "brand": brandName.lower(),       
            "category": categoryName.lower(), 
            "specs": specs_combined,     
            "desc": desc_have_name.lower()         
        },
        "images": image_list
    }



