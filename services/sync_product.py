from services.database import db_manager, ImageSchema, ProductSchema
import numpy as np
from services.processing import encode_text, encode_image_from_url, create_product_embedding_data, encode_short_text, normalize
from config import W_BRAND, W_CATE, W_SPECS, W_DESC


def sync_product_data(product_data_dict):
    tbl_detail = db_manager.get_table('products')
    tbl_images = db_manager.get_table('images')
    if not tbl_detail or not tbl_images:
        return {"status": "Database table not found."}
    
    product_embedding_data = create_product_embedding_data(product_data_dict)

    # Tạo vector cho ảnh
    image_vectors = []
    for img_url in product_embedding_data['images']:
        vec = encode_image_from_url(img_url)
        if vec is None:
            continue  #bỏ qua nếu lấy vector embed ảnh thất bại
        image_vectors.append(ImageSchema(
            spu=product_data_dict['spu'],
            vector=vec
        ))
    
    # Tạo vector cho sản phẩm
    search_text = product_embedding_data['search_text']
    vector_search = encode_text(search_text)

    parts = product_embedding_data['parts']

    v_brand = encode_short_text(parts['brand'])
    v_cate = encode_short_text(parts['category'])
    v_specs = encode_short_text(parts['specs'])
    v_desc = encode_text(parts['desc'])

    v_brand = normalize(v_brand) * W_BRAND
    v_cate  = normalize(v_cate)  * W_CATE
    v_specs = normalize(v_specs) * W_SPECS
    v_desc  = normalize(v_desc)  * W_DESC

    v_recs = np.concatenate([v_brand, v_cate, v_specs, v_desc])

    product_record = ProductSchema(
        spu=product_data_dict['spu'],
        vector_search=vector_search,
        vector_recs=v_recs,
        full_text=product_embedding_data['search_text']
    )

    # Upsert product detail
    tbl_detail.delete(f"spu = '{product_data_dict['spu']}'")
    tbl_detail.add([product_record])    # Upsert product images
    tbl_images.delete(f"spu = '{product_data_dict['spu']}'")
    tbl_images.add(image_vectors)
    
    return {"status": "Product synchronized successfully."}

def delete_product_sync(product_spu: str):
    tbl_detail = db_manager.get_table('products')
    tbl_images = db_manager.get_table('images')
    if not tbl_detail or not tbl_images:
        return {"status": "Database table not found."}
    
    tbl_detail.delete(f"spu = '{product_spu}'")
    tbl_images.delete(f"spu = '{product_spu}'")
    
    return {"status": f"Product {product_spu} deleted from sync successfully."}
