from typing import Optional
from pydantic import BaseModel

class ProductType(BaseModel):
    Classification: str
    FClassification: str
    Count: str
    Name: str

class ProductComment(BaseModel):
    CommentCountStr: str
    AfterCountStr: str # 追评
    DefaultGoodCountStr: str
    GeneralCountStr: str
    GoodCountStr: str
    PoorCountStr: str
    VideoCountStr: str
    SkuId: str

class Product(BaseModel):
    class Shop(BaseModel):
        shop_name: str
        good_shop: str

    ad_title: str
    good_rate: str
    image_url: str
    link_url: str
    sku_id: str
    pc_price: str
    shop_link: Shop

    comment: Optional[ProductComment]

