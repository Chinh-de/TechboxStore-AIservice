from fastapi import APIRouter, HTTPException, Header
from schemas import ProductResponse
from services.sync_product import sync_product_data, delete_product_sync
from config import SYNC_API_KEY

router = APIRouter(
    prefix="/sync/products",
    tags=["sync"],
)

def check_api_key(api_key: str):
    if api_key != SYNC_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@router.post("")
def sync_products(
    product: ProductResponse,
    x_api_key: str = Header(..., alias="X-API-Key")  # Lấy từ header X-API-Key
):
    check_api_key(x_api_key)
    sync_product_data(product.model_dump())

    return {"status": "Products synchronized successfully"}

@router.delete("/{product_spu}")
def delete_product_sync_endpoint(
    product_spu: int,
    x_api_key: str = Header(..., alias="X-API-Key")  # Lấy từ header X-API-Key
):
    check_api_key(x_api_key)

    print(f"Deleting sync for product SPU: {product_spu}")
    delete_product_sync(product_spu)

    return {"status": f"Product {product_spu} deleted from sync successfully"}
