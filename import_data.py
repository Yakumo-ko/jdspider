import asyncio
import pymysql
import json
import random
import os

from model import Product, ProductComment
from spider import getProductType


def createTable() -> None:
	db = pymysql.connect(host="192.168.10.9", user="springuser", passwd="123456", database="spring", port=5252)

	cursor = db.cursor()
	create_sql = """
        CREATE TABLE `{}`  (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `gid` bigint(11) NULL DEFAULT NULL,
        `action` int(11) NULL DEFAULT NULL,
        `date` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
        PRIMARY KEY (`id`) USING BTREE
        ) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;
    """

	for i in range(1, 301):
		s = "act_u{}".format(i)
		cursor.execute(create_sql.format(s))
		db.commit()


async def importType(url: str) -> None:
    sql: str = """INSERT INTO `spring`.`classification` 
        (`Fclassification`, `classification`, `name`, `field`) 
        VALUES ({f},  {c}, '{name}', '{field}')"""
    db = pymysql.connect(
            host="localhost", 
            user="springuser", 
            passwd="123456", 
            database="spring", 
            port=5252
        )

    types = await getProductType(url)
    assert types != None
    for i in types:
        db.cursor().execute(sql.format(
            f = i.FClassification,
            c = i.Classification,
            name = i.Name,
            field = i.Field))
        db.commit()

def  toNum(num: str) -> int:
    num = num.replace('+', '');
    if num.find('万') >0:
        return int(float(num.replace('万', '')) * 10000) + random.randint(0, 9999);
    return int(num) + random.randint(0, int(num)//10);


def importData(path: str, gtype: int) -> None: 
    comment_sql: str = """insert into `spring`.`comment`
                (`sku_id`, `type` ,`after`, `comment_count`, `default_good`,
                `gerneral`, `good`, `poor`, `video`)
                values({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})
                """

    product_sql: str = """insert into `spring`.`product`
                (`sku_id`, `type`, `image_url`, `link_url`, `price`,
                `shop`, `shop_url`, `title`)
                values({0}, {1}, "{2}", "{3}", {4}, "{5}", "{6}", "{7}")
                """
    db = pymysql.connect(
            host="localhost", 
            user="springuser", 
            passwd="123456", 
            database="spring", 
            port=5252
        )

    json_data = None
    with open(path, mode='r', encoding='utf-8') as f:
        json_data = json.load(f)['data']
    

    cursor = db.cursor()
    a = set()
    count: int = 0
    for item in json_data:
        t = Product.parse_obj(item)
        if t.sku_id in a:
            count += 1
            continue
        a.add(t.sku_id)

        cursor.execute(product_sql.format 
                       (int(t.sku_id), 
                        gtype,
                        t.image_url,
                        t.link_url,
                        float(t.pc_price),
                        t.shop_name,
                        t.shop_url,
                        t.title
                        ))

        cursor.execute(comment_sql.format 
                       (int(t.comment.SkuId),
                        gtype,
                        toNum(t.comment.AfterCountStr),
                        toNum(t.comment.CommentCountStr),
                        toNum(t.comment.DefaultGoodCountStr),
                        toNum(t.comment.GeneralCountStr),
                        toNum(t.comment.GoodCountStr),
                        toNum(t.comment.PoorCountStr),
                        toNum(t.comment.VideoCountStr)
                           ))
    db.commit()
    print(f"all {count}, valid: {len(a)} in {path}")


with open('./tmp.txt') as f:
    while f.readable():
        text = f.readline().split('-')
        print(text)
        if len(text) == 0:
            break
        id = int(text[0])
        name = text[1].replace('/', '-').replace('\n', '')
        importData("./data/悠闲零食/" + name + ".json", id)






    

