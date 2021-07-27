import cx_Oracle
import mybatis_mapper2sql
import configparser
from datetime import datetime
from dateutil.relativedelta import relativedelta


def buySort(buyList: list):
    if buyList:
        return {'buy_seq': buyList[0],
                'menu_seq': buyList[1],
                'buy_cnt': buyList[2],
                'in_date': buyList[3],
                'in_user_id': buyList[4],
                'up_date': buyList[5],
                'up_user_id': buyList[6]}
    else:
        return None


class DaoBuy:
    def __init__(self, config_path='config.ini', xml_path='dao/buy.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]

    def genBuySeq(self):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "genBuySeq")
        self.cs.execute(sql)
        return self.cs.fetchone()[0]

    def select(self, buy_seq, menu_seq, buy_cnt, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        self.cs.execute(sql, (buy_seq, menu_seq, buy_cnt, in_date, in_user_id, up_date, up_user_id))
        return list(map(buySort, self.cs.fetchall()))

    def insert(self, buy_seq, menuList, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        count = 0
        for menu in menuList:
            self.cs.execute(sql, (buy_seq, menu['menu_seq'], menu['count'], owner_seq, owner_seq))
            count += self.cs.rowcount
        self.conn.commit()
        return count

    def delete(self, buy_seq, menu_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete")
        self.cs.execute(sql, (buy_seq, menu_seq))
        self.conn.commit()
        return self.cs.rowcount

    def store_sales(self):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "store_sales")
        rs = self.cs.execute(sql)
        list = []
        for record in rs:
            list.append({'store_name': record[0],
                         'store_sales': record[1]})
        return list

    def sixMonthStoreSales(self):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "sixMonthStoreSales")
        self.cs.execute(sql)
        res = self.cs.fetchall()

        if not res:
            return None
        saleList = [['월'], [res[0][2]], [res[1][2]], [res[2][2]], [res[3][2]], [res[4][2]], [res[5][2]]]
        for i in range(0, len(res), 6):
            saleList[0].append(res[i][1])
            saleList[1].append(res[i][3])
            saleList[2].append(res[i+1][3])
            saleList[3].append(res[i+2][3])
            saleList[4].append(res[i+3][3])
            saleList[5].append(res[i+4][3])
            saleList[6].append(res[i+5][3])

        return saleList


if __name__ == "__main__":
    dao = DaoBuy(config_path='../config.ini', xml_path='buy.xml')
    saleList = dao.sixMonthStoreSales()

