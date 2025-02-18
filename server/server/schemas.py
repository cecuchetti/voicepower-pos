from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from pydantic import field_validator

class ProductBase(BaseModel):
    name: str
    price: float
    category: str
    stock: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SaleItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class SaleItem(SaleItemBase):
    id: int
    sale_id: int

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    total: float
    notes: Optional[str] = None

class SaleCreate(SaleBase):
    items: List[SaleItemBase]

class Sale(SaleBase):
    id: int
    date: datetime
    items: List[SaleItem]

    class Config:
        from_attributes = True

class CartItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    quantity: float
    unit_price: float

class CartItem(CartItemCreate):
    id: int
    cart_id: int

    class Config:
        from_attributes = True

class CartBase(BaseModel):
    status: str = "active"

class CartCreate(CartBase):
    items: List[CartItemCreate] = []

class Cart(CartBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[CartItem]

    class Config:
        from_attributes = True

class CartItemDetail(CartItem):
    product: Product
    total: float

    @field_validator('total')
    def calculate_total(cls, v, values):
        return values.data['quantity'] * values.data['unit_price']

class CartDetail(Cart):
    items: List[CartItemDetail]
    total: float
    item_count: int

    @field_validator('total')
    def calculate_total(cls, v, values):
        return sum(item.total for item in values.data['items'])
    
    @field_validator('item_count')
    def count_items(cls, v, values):
        return sum(item.quantity for item in values.data['items']) 