import cx_Oracle
import mybatis_mapper2sql
import configparser


def categorySort(categoryList: list):
    if categoryList:
        return {"cate_seq": categoryList[0],
                "owner_seq": categoryList[1],
                "cate_name": categoryList[2],
                "cate_content": categoryList[3],
                "cate_display_yn": categoryList[4],
                "attach_path": categoryList[5],
                "attach_file": categoryList[6],
                "in_date": categoryList[7],
                "in_user_id": categoryList[8],
                "up_date": categoryList[9],
                "up_user_id": categoryList[10]}
    else:
        return None 


class DaoCategory:
    def __init__(self, config_path='config.ini', xml_path='dao/category.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]

    def selectAll(self, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "selectAll")
        self.cs.execute(sql, (owner_seq,))
        return list(map(categorySort, self.cs.fetchall()))

    def selectYList(self, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "selectYList")
        self.cs.execute(sql, (owner_seq,))
        return list(map(categorySort, self.cs.fetchall()))

    def selectKiosk(self, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "selectKiosk")
        self.cs.execute(sql, (owner_seq,))
        return list(map(categorySort, self.cs.fetchall()))



    def select(self, owner_seq, cate_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        self.cs.execute(sql, (owner_seq, cate_seq))
        return categorySort(self.cs.fetchone())

    def myinsert(self, owner_seq, cate_name, cate_content, cate_display_yn, attach_path, attach_file):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        self.cs.execute(sql, (owner_seq, cate_name, cate_content, cate_display_yn, attach_path, attach_file, owner_seq, owner_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def myupdate(self, cate_seq, owner_seq, cate_name, cate_content, cate_display_yn, attach_path, attach_file, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "update")
        self.cs.execute(sql, (owner_seq, cate_name, cate_content, cate_display_yn, attach_path, attach_file, up_user_id, cate_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def mydelete(self, cate_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete")
        self.cs.execute(sql, (cate_seq,))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def del_img(self, cate_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "del_img")
        self.cs.execute(sql, (cate_seq,))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt
        pass


if __name__ == "__main__":
    dao = DaoCategory(config_path='../config.ini', xml_path='category.xml')
    list = dao.mydelete("4")
#     list = dao.myupdate("21", "1", "66", "1", "1", "1", "1", " ", "1", " ", "1")
#     list = dao.myinsert("백종원", "1", "1", "1", "1", "1", "1", " ", "1", " ", "1")
#     print(list)
