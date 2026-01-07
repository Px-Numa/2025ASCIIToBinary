#################################################################
#2024/07/26
#ItoNatsuki
#pythonでpostgresqlにアクセス
#################################################################


import psycopg2
import time 

"""
conn = psycopg2.connect(
    host="192.168.1.2",
    database="test3",
    user="odd",
    password="odd"
)
"""
conn = psycopg2.connect(
    host="192.168.1.2",
    database="management_db",
    user="odd",
    password="odd"
)



cur = conn.cursor()

def create():
    #cur.execute("""
    #   CREATE TABLE test_ito (id SERIAL PRIMARY KEY,name VARCHAR(255),email VARCHAR(255)
    #    )
    #""")

    #cur.execute("""
    #   CREATE TABLE test_qr (seizou_date VARCHAR(255), product_id VARCHAR(255),  lot_id VARCHAR(255) )
    #""")
    
    ##エラーログテーブル
    #cur.execute("""
    #   CREATE TABLE t_errorlog (error_number SERIAL PRIMARY KEY, errored_time timestamp,  error_status boolean, error_id INTEGER)
    #""")
    
    ##配送テーブル
    #cur.execute("""
    #   CREATE TABLE ito_deliver (deliver_id SERIAL PRIMARY KEY, deliver_schedule timestamp, order_id INTEGER, deli_status_id INTEGER, delivered_date timestamp)
    #""")
    
    ##製造情報テーブル
    #cur.execute("""
    #   CREATE TABLE ito_manufacture_info (product_id VARCHAR(255), lot_id VARCHAR(255), manufacture_day timestamp, lot_status INTEGER)
    #""")
    
    ##配送登録テーブル
    #cur.execute("""
    #   CREATE TABLE ito_deli_regi (date timestamp, order_id INTEGER, product_id INTEGER, product_num INTEGER, issue_num INTEGER)
    #""")
    
    ##出庫登録テーブル
    #cur.execute("""
    #   CREATE TABLE ito_issue_regi (date timestamp, order_id INTEGER, product_id INTEGER, issue_num INTEGER)
    #""")
    
    ##生産登録テーブル
    cur.execute("""
       CREATE TABLE ito_product_regi (date timestamp, product_id INTEGER, product_num INTEGER)
    """)
    
    ##配送登録テーブル
    #cur.execute("""
    #   CREATE TABLE t_deliver (deliver_schedule timestamp, order_id INTEGER, product_id INTEGER)
    #""")

    #会社テーブル
    #cur.execute("""
    #   CREATE TABLE ito_companys (company_id VARCHAR(255) PRIMARY KEY,company_name VARCHAR(255),company_address VARCHAR(255))
    #""")

    #商品テーブル
    #cur.execute("""
    #   CREATE TABLE ito_products (product_id VARCHAR(255) PRIMARY KEY,product_name VARCHAR(255), product_price INTEGER)
    #""")

    #受注テーブル
    #cur.execute("""
    #   CREATE TABLE ito_orders (order_id SERIAL PRIMARY KEY, order_date DATE, company_id VARCHAR(255), order_price INTEGER)
    #""")

    #受注詳細テーブル
    #cur.execute("""
    #   CREATE TABLE ito_orders_detail (order_detail_id SERIAL PRIMARY KEY, order_id INTEGER, company_id VARCHAR(255), product_id VARCHAR(255), quantity INTEGER)
    #""")

    #cur.execute("drop table if exists ito_product_regi")

    conn.commit()


def insert():
    #データを挿入
    #cur.execute("""
    #    INSERT INTO test_ito (name, email) VALUES (%s, %s)""", ("Natsuki Ito", "johndoe@example.com"))

    #cur.execute("""
    #    INSERT INTO test_qr VALUES ('20241001', 'ob10', '0001')""")
       
    time_stamp = time.strftime('%Y-%m-%d')

    print(time_stamp)
    
    ##エラーログ挿入
    #cur.execute(
    #    "INSERT INTO t_errorlog (error_id, errored_time, error_status) VALUES (1, '" + time_stamp + "', TRUE)")

    #配送情報挿入
    #cur.execute(
    #    "INSERT INTO ito_deliver (deliver_schedule, order_id, deli_status_id) VALUES ('" + time_stamp + "', 3, 1)"
    #)
    
    #製造情報挿入
    cur.execute(
        "INSERT INTO t_manufacture_info VALUES (1, '00001', '2024-11-29', 1)"
    )
    

    #会社テーブル
    #cur.execute("""
    #    INSERT INTO ito_companys VALUES ('ktnkd', '関東職業能力開発大学校', '栃木県小山市')""")

    #商品テーブル
    #cur.execute("""
    #    INSERT INTO ito_products VALUES ('o_1', 'お魚箱', 1000)""")
    
    #受注テーブル
    #cur.execute("""
    #    INSERT INTO ito_orders (order_date, company_id, order_price) VALUES (now(), 'ktnkd', 2000)""")
    
    #受注詳細テーブル
    #cur.execute("""
    #    INSERT INTO ito_orders_detail (order_id, company_id, product_id, quantity) VALUES (3, 'ktnkd', 'o_2', 4)""")
    
    

    conn.commit()

def select():
    #cur.execute("SELECT * FROM m_product")
    #cur.execute("SELECT * FROM t_errorlog")
    #cur.execute("SELECT * FROM t_loginlog")
    #cur.execute("SELECT * FROM test_ito")
    #cur.execute("SELECT * FROM test_qr")
    #cur.execute("SELECT * FROM ito_companys")
    #cur.execute("SELECT * FROM ito_products")
    #cur.execute("SELECT * FROM ito_orders")
    #cur.execute("SELECT * FROM ito_orders_detail")
    #cur.execute("SELECT * FROM ito_deliver")
    #cur.execute("SELECT * FROM ito_manufacture_info")
    #cur.execute("SELECT order_id, (SELECT company_name FROM ito_companys WHERE company_id ='ktnkd') FROM ito_orders WHERE company_id = 'ktnkd'")
    
    #cur.execute("DELETE FROM t_manufacture_info")
    #onn.commit()
    
    #cur.execute("SELECT * from t_orderline WHERE NOT EXISTS (SELECT * from t_deliver where t_orderline.order_id = t_deliver.order_id and (deliver_status = 1 or deliver_status = 2));")
    cur.execute("SELECT * FROM m_product")
    #cur.execute("SELECT * FROM t_deliver")
    #cur.execute("SELECT * FROM t_manufacture_info")
    #cur.execute("SELECT * FROM t_order")
    #cur.execute("select orderer_name from (m_orderer inner join t_order on (m_orderer.orderer_id = (select orderer_id from t_order where order_id = 2)));")
    #cur.execute("select orderer_id from t_order where order_id = 1")
    
    rows = cur.fetchall()

    for row in rows:
        print(row)

def update():
    #cur.execute("update t_deliver set deliver_status = 0")
    cur.execute("update t_errorlog set error_status = TRUE")
    #cur.execute("update t_manufacture_info set lot_status = 1")
    #cur.execute("update m_product set product_quantity = product_quantity - 1 where product_id = 3")
    conn.commit()
def delete():
    cur.execute("""
        delete from t_deliver
    """)
    conn.commit()


#create()
#insert()
#delete()
update()
select()


