import asyncio
from asyncio.tasks import create_task
from typing import Coroutine, List
from model import ProductType

from spider import (getProductList, getProductType, combineds)

#product_type_url = "https://search.jd.com/category.php?keyword=食品&stop=1&qrst=1&vt=2&suggest=1.his.0.0&pvid=556773238ff942368a86481067361e59&cid3=31647&cid2=1583&c=all"
product_type_url  = "https://search.jd.com/category.php?keyword=%E9%A3%9F%E5%93%81&stop=1&qrst=1&vt=2&suggest=1.his.0.0&pvid=24c4e72481ec4aa69aab5da994f6fe4c&cid3=5020&cid2=5019&c=all"

async def main(page: int = 1):
    types = await getProductType(product_type_url)

    async_funcs = []
    for i in types:
       async_funcs.append(asyncio.create_task(combineds(
                f"./data/{i.Name.replace('/', '-')}.json", 
                i, 
                page, 
                '食品'
            )))
    await asyncio.gather(*async_funcs) 


asyncio.run(main(50))
"""
t = ProductType.parse_obj({
    "Classification": 5019,
    "FClassification": 0,
    "Count": 100000, 
    "Name": '进口食品' 
    })


asyncio.run(combineds(
                f"./data/{t.Name.replace('/', '-')}.json", 
                t, 
                50,
                '食品'

    ))
"""
