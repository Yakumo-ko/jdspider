import asyncio
import os
from typing import Any, Dict, List, Optional, TypeVar, Union
import json
import random
import time
import logging
from bs4 import BeautifulSoup 
from bs4.element import Tag
from pydantic import BaseModel

import httpx
from model import (AdProduct, 
                   ProductType, 
                   ProductComment, 
                   Product)

T = TypeVar("T", bound=BaseModel)

headers = {
    "Referer": "https://search.jd.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41",
    "sec-ch-ua-platform": "Windows"
}

async def request(
        url: str, 
        headers: Optional[Dict[str, str]] = headers
    ) -> httpx.Response:
    re = httpx.get(url=url, headers=headers)
    if re.status_code != 200:
        logging.error("stauts: %d %s" %(re.status_code, url))
        raise 
    return re

async def requestJson(
        url: str, 
        headers: Optional[Dict[str, str]] = headers
    )->Dict[Any, Any]:
    return (await request(url, headers)).json()

async def requestHtml(
        url: str, 
        headers: Optional[Dict[str, str]] = headers
        ) -> str:
    return (await request(url, headers)).text

async def wrap(model: T, data: Dict[Any, Any]) -> List[T]:
    return [model.parse_obj(item) for item in data]

async def writeJSON(path: str, data: List[Product]) -> None:
    with open(path, mode="a+", encoding="utf-8") as f:
        if f.tell() == 0:
            res = {
                "data": [i.dict() for i in data]
                }
            f.write(json.dumps(res, ensure_ascii=False))
        else:
            f.seek(0, os.SEEK_SET)
            t = json.load(f)
            t['data'] += [i.dict() for i in data]
            f.truncate(0)
            f.seek(0, os.SEEK_SET)
            f.write(json.dumps(t, ensure_ascii=False))

async def getAdProductInfo(
        product_type: Union[str, int], 
        page: Union[str, int]
    ) -> List[AdProduct]:

    get_product_url = "https://search-x.jd.com/Search?area=20&enc=utf-8&keyword=食品&adType=7&urlcid3={product_type}&page={page}&ad_ids=291:19&xtest=new_search&_={timestamp}"

    data = await requestJson(
            get_product_url.format(
                product_type = product_type, 
                page = page, 
                timestamp = int(time.time())
                ),
            headers=headers
            )    
    return await wrap(AdProduct, data['291']) 

async def getProductInfo(html: Tag) -> Product:
    p_img = html.find('div', class_='p-img')
    p_price = html.find('div', class_='p-price')
    p_shop = html.find('div', class_='p-shop')
    return Product.parse_obj({
            "sku_id": html['data-sku'],
            "title": p_img.a['title'],
            "link_url": p_img.a['href'],
            "image_url": p_img.a.img['data-lazy-img'],
            "pc_price": p_price.strong.i.text,
            "shop_url": p_shop.span.a['href'] if p_shop.find('a') else '',
            "shop_name": p_shop.span.a['title'] if p_shop.find('a') else '',
        })

async def getProductList(
        keyword: str,
        cid2: Union[str, int],
        cid3: Union[str, int],
        page: Union[str, int]
    ) -> List[Product]:
    url = "https://search.jd.com/s_new.php?keyword={kw}&cid3={cid3}&cid2={cid2}&page={page}"
    row = await requestHtml(
            url.format(kw = keyword, cid2 = cid2, cid3 = cid3, page = page) 
        )
    list = BeautifulSoup(row, "lxml").find_all("li")
    assert len(list) > 0, f"error: {row} in {url.format(kw = keyword, cid2 = cid2, cid3 = cid3, page = page)}"

    products = []
    for item in list:
        if item['ware-type'] == '0':
            continue
        products.append(await getProductInfo(item))
    return products

async def getProductComment(
        gid: List[str]
    ) -> List[ProductComment]:
    product_comment_url = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds={args}&_={timestamp}"
    args = ",".join(gid)
    data = await requestJson(
            product_comment_url.format(
                args = args,
                timestamp = int(time.time())
                ) 
            )
    return await wrap(ProductComment, data['CommentsCount']) 
    
async def getProductType(url) -> List[ProductType]:
    data = await requestJson(url)
    return await wrap(ProductType, data['data']) 

Page = TypeVar('Page', str, int)

async def combined(
        path: str,
        p_type: ProductType, 
        page: Page,
        keyword: str
    ) -> bool:
    products = await getProductList(keyword, 
            p_type.FClassification, 
            p_type.Classification, 
            page) 
    if len(products) == 0:
        logging.error(
                "can't get product on page %s in %s" %(page, p_type))
        return False
    args = [i.sku_id for i in products]
    comment = await getProductComment(args)
    if len(comment) == 0:
        logging.error(
                "can't get comment for {args} on page {page} in {type}".format(
                    args = args,
                    page = page,
                    type = p_type 
                    )
                )
        return False
    
    for index in range(len(products)):
        products[index].comment = comment[index]

    await writeJSON(path, products)
    return True

async def combineds(
        path: str,
        p_type: ProductType,
        start_page: Page,
        page: Page,
        keyword: str,
    ) -> None:
    for i in range(int(start_page), int(page)+1):
        print("start %s page: %s cid3: %s" %(p_type.Name, i, p_type.Classification))
        if i * 25 > int(p_type.Count):
            print("%s > %s, finish this task id: %s" %(i * 25, p_type.Count, p_type.Classification))
            break;
        res = await combined(path, 
                            p_type, 
                            i, 
                            keyword)
        #logging.info("sucess page %s in %s on %s" %(page, path, type.Classification))
        if res:
            print("sucess page %s in %s on %s" %(i, path, p_type.Classification))
        await asyncio.sleep(random.randint(5, 10))        

