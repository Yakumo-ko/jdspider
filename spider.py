from typing import List, Optional, Union
import os
import asyncio
import json
import time
import logging

import requests
import httpx
from pydantic import BaseModel

class ProductType(BaseModel):
    Classification: str
    FClassification: str
    Count: str

class ProductComment(BaseModel):
    CommentCountStr: str
    AfterCountStr: str # 追评
    DefaultGoodCountStr: str
    GeneralCountStr: str
    GoodCountStr: str
    PoorCountStr: str
    VideoCountStr: str
    ProductId: int

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





headers = {
    "Referer": "https://search.jd.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41",
    "sec-ch-ua-platform": "Windows"
}


async def writeJSON(path: str, data: List[Product]) -> None:
    with open(path, mode="w+", encoding="utf-8") as f:
        res = {
                "data": [i.dict() for i in data]
            }
        f.write(json.dumps(res, ensure_ascii=False))

async def getProductInfo(
        product_type: Union[str, int], 
        page: Union[str, int]
    ) -> Union[List[Product], None]:

    get_product_url = "https://search-x.jd.com/Search?area=20&enc=utf-8&keyword=食品&adType=7&urlcid3={product_type}&page={page}&ad_ids=291:19&xtest=new_search&_={timestamp}"

    re = httpx.get(
            get_product_url.format(
                product_type = product_type, 
                page = page, 
                timestamp = int(time.time())
                    ),
            headers=headers
            )    
    
    if re.status_code!=200:
        logging.error("stauts: %d", re.status_code)
        return None
    
    data = re.json()['291']
    return await wrapProduct(data)

async def wrapProduct(data: dict) -> List[Product]:
    return [Product.parse_obj(item) for item in data]

async def getProductComment(
        gid: List[str]
    ) -> Union[List[ProductComment], None]:
    product_comment_url = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds={args}&_={timestamp}"
    args = ",".join(gid)
    re = httpx.get(
            product_comment_url.format(
                args = args,
                timestamp = int(time.time())
                ), 
            headers = headers
            )
    if re.status_code != 200:
        return None
    return await wrapComment(re.json()['CommentsCount'])

async def wrapComment(data: dict) -> List[ProductComment]:
    return [ProductComment.parse_obj(item) for item in data]
    
async def getProductType(url):
    re = httpx.get(product_type_url, headers=headers)
    if re.status_code != 200:
        return None
    return await wrapProductType(re.json()['data'])

async def wrapProductType(data: dict) -> List[ProductType]:
    return [ProductType.parse_obj(item) for item in data]

product_type_url = "https://search.jd.com/category.php?keyword=食品&stop=1&qrst=1&vt=2&suggest=1.his.0.0&pvid=556773238ff942368a86481067361e59&cid3=31647&cid2=1583&c=all"
async def main():
    a = await getProductType(product_type_url)
    print(a)

asyncio.run(main())




