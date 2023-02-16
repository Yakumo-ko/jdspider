import asyncio
from typing import Coroutine, List

from spider import (getProductType, combineds)

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

    for i in types:
        print("start %s" %(i.Name))
        await combineds(f"./data/{i.Name.replace('/', '-')}.json", i, 1)

#asyncio.run(main())

url = "https://search.jd.com/s_new.php?keyword=食品&cid3=1595&cid2=1583&page=1&s=0"

import httpx
from bs4 import BeautifulSoup

headers = {
    "Referer": "https://search.jd.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41",
    "sec-ch-ua-platform": "Windows"
}

re = httpx.get(url, headers=headers)
print(re.text)
