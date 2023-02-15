import asyncio
from typing import Any, Dict, List, Optional, TypeVar, Union
import json
import time
import logging
from pydantic import BaseModel

import httpx
from model import (Product, ProductType, ProductComment)

T = TypeVar("T", bound=BaseModel)

headers = {
    "Referer": "https://search.jd.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41",
    "sec-ch-ua-platform": "Windows"
}

async def request(
        url: str, 
        headers: Optional[Dict[str, str]] = headers
    ) -> Union[Dict[Any, Any], None]:
    re = httpx.get(url = url, headers=headers)
    if re.status_code != 200:
        logging.error("stauts: %d %s" %(re.status_code, url))
        return None
    return re.json()

async def wrap(model: T, data: Dict[Any, Any]) -> List[T]:
    return [model.parse_obj(item) for item in data]

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

    data = await request(
            get_product_url.format(
                product_type = product_type, 
                page = page, 
                timestamp = int(time.time())
                ),
            headers=headers
            )    
    return await wrap(Product, data['291']) if data != None else None

async def getProductComment(
        gid: List[str]
    ) -> Union[List[ProductComment], None]:
    product_comment_url = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds={args}&_={timestamp}"
    args = ",".join(gid)
    data = await request(
            product_comment_url.format(
                args = args,
                timestamp = int(time.time())
                ), 
            headers = headers
            )
    if data == None:
        return None
    return await wrap(ProductComment, data['CommentsCount']) 
    
async def getProductType(url) -> Union[List[ProductType], None]:
    data = await request(url, headers=headers)
    return await wrap(ProductType, data['data']) if data != None else None

async def combined(
        path: str,
        product_type: Union[str, int], 
        page: Union[str, int]
    ) -> None:
    products = await getProductInfo(product_type, page)
    if products == None:
        logging.error(
                "can't get product on page %s in %s" %(page, product_type))
    args = [i.sku_id for i in products]
    comment = await getProductComment(args)
    if comment == None:
        logging.error(
                "can't get comment for {args} on page {page} in {type}".format(
                    args = args,
                    page = page,
                    type = product_type
                    )
                )
    
    for index in range(len(products)):
        if products[index].sku_id == comment[index].SkuId:
            products[index].comment = comment[index]
        else:
            raise

    await writeJSON(path, products)

async def combineds(
        path: str,
        product_type: Union[str, int], 
        page: Union[str, int]
    ) -> None:
    for i in range(1, int(page)+1):
        await combined(path, product_type, page)
        logging.info("sucess page %s in %s on %s" %(page, path, product_type))
        await asyncio.sleep(5)        

