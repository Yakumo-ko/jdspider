import asyncio
from typing import Coroutine
from spider import (getProductType, combineds)

product_type_url = "https://search.jd.com/category.php?keyword=食品&stop=1&qrst=1&vt=2&suggest=1.his.0.0&pvid=556773238ff942368a86481067361e59&cid3=31647&cid2=1583&c=all"

async def main(page: int = 1):
    types = await getProductType(product_type_url)

    async_funcs: List[Coroutine] = []
    for i in types:
        if page * 30 > int(i.Count):
            page = int(i.Count) // 30 + 1
        async_funcs.append(
                combineds(
                    f"./data/{i.Name.replace('/', '-')}.json", 
                    i.Classification, 
                    page
                )
            )

    asyncio.gather(*async_funcs) 

asyncio.run(main())
