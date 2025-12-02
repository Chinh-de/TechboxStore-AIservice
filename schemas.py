from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: List[ChatMessage] = []

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

class RecRequest(BaseModel):
    spus: List[str]
    top_k: int = 10




class ProductAttribute(BaseModel):
    id: int
    name: str
    value: str


class VariationImage(BaseModel):
    id: int
    imageUrl: str


class VariationAttribute(BaseModel):
    id: int
    name: str
    value: str


class ProductVariation(BaseModel):
    id: int
    variationName: str
    sku: str
    price: float
    availableQuantity: int
    salePrice: Optional[float]
    discountType: Optional[str]
    discountValue: Optional[float]
    images: List[VariationImage]
    attributes: List[VariationAttribute]


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    categoryId: int
    categoryName: str
    spu: str
    brandId: int
    brandName: str
    imageUrl: str
    imagePublicId: Optional[str]
    warrantyMonths: int
    averageRating: float
    totalRatings: int
    displayOriginalPrice: float
    displaySalePrice: float
    discountType: Optional[str]
    discountValue: Optional[float]

    attributes: List[ProductAttribute]
    variations: List[ProductVariation]