import asyncio

from spider import (getProductType, combineds)


async def main(url: str, start_page: int = 1, page: int = 1):
    types = await getProductType(url)
    """
    for item in types:
        print(f"{item.Classification}-{item.Name}")
    return 
    """
    async_funcs = []
    for i in types:
       async_funcs.append(asyncio.create_task(combineds(
                f"./data/{i.Name.replace('/', '-')}.json", 
                i, 
                start_page,
                page, 
                '食品'
            )))
    await asyncio.gather(*async_funcs) 

product_type_url = "https://search.jd.com/category.php?keyword=食品&stop=1&qrst=1&vt=2&suggest=1.his.0.0&pvid=7a93d8c0865947a994f7f2abf0494334&cid3=31647&cid2=1583&c=all"

#asyncio.run(main(product_type_url, 1, 35))
asyncio.run(main(product_type_url, 37, 100))

