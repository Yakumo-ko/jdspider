import asyncio
from typing import Coroutine, List

from spider import (getProductList, getProductType, combineds)

product_type_url = "https://search.jd.com/category.php?keyword=食品&stop=1&qrst=1&vt=2&suggest=1.his.0.0&pvid=556773238ff942368a86481067361e59&cid3=31647&cid2=1583&c=all"

"""
async def main(page: int = 1):
    types = await getProductType(product_type_url)

    async_funcs: List[Coroutine] = []
    for i in types:
        if page * 30 > int(i.Count):
            page = int(i.Count) // 30 + 1
        async_funcs.append(
                combineds(
                    f"./data/{i.Name.replace('/', '-')}.json", 
                    i, 
                    page
                )
            )

    asyncio.gather(*async_funcs) 
"""
async def main(page: int = 1):
    types = await getProductType(product_type_url)

    async_funcs: List[Coroutine] = []
    for i in types:
       async_funcs.append(combineds(
                f"./data/{i.Name.replace('/', '-')}.json", 
                i, 
                page, 
                '食品'
            ))
    asyncio.gather(*async_funcs) 

#asyncio.run(main())

url = "https://search.jd.com/s_new.php?keyword=食品&cid3=1595&cid2=1583&page=1&s=0"

async def tmp():
    types = await getProductType(product_type_url)
    await combineds(
                f"./data/{types[0].Name.replace('/', '-')}.json", 
                types[0], 
                50,
                '食品'
                )

asyncio.run(main())
