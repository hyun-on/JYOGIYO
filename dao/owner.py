import cx_Oracle
import mybatis_mapper2sql
import configparser


class DaoOwner:
    def __init__(self, config_path='config.ini', xml_path='dao/owner.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]

    def owner_seq_gen(self):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "owner_seq_gen")
        self.cs.execute(sql)
        return self.cs.fetchone()[0]

    def selectAll(self):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "selectAll")
        rs = self.cs.execute(sql)
        list = []
        for record in rs:
            list.append({'owner_seq': record[0], 'owner_name': record[1], 'owner_id': record[2], 'owner_pwd': record[3],
                         'owner_str_name': record[4], 'owner_str_num': record[5], 'owner_str_tel': record[6], 'owner_add1': record[7],
                         'owner_add2': record[8], 'logo_path': record[9], 'logo_file': record[10], 'admin_yn': record[11],
                         'in_date': record[12], 'in_user_id': record[13], 'up_date': record[14], 'up_user_id': record[15]})
        return list

    def select(self, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        rs = self.cs.execute(sql, (owner_seq,))
        obj = None
        for record in rs:
            obj = {'owner_seq': record[0], 'owner_name': record[1], 'owner_id': record[2], 'owner_pwd': record[3],
                   'owner_str_name': record[4], 'owner_str_num': record[5], 'owner_str_tel': record[6], 'owner_add1': record[7],
                   'owner_add2': record[8], 'logo_path': record[9], 'logo_file': record[10], 'admin_yn': record[11],
                   'in_date': record[12], 'in_user_id': record[13], 'up_date': record[14], 'up_user_id': record[15]}
        return obj

    def select_login(self, owner_id, owner_pwd):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select_login")
        rs = self.cs.execute(sql, (owner_id, owner_pwd))
        obj = None
        for record in rs:
            obj = {'owner_seq': record[0], 'owner_name': record[1], 'owner_id': record[2], 'owner_pwd': record[3],
                   'owner_str_name': record[4], 'owner_str_num': record[5], 'owner_str_tel': record[6], 'owner_add1': record[7],
                   'owner_add2': record[8], 'logo_path': record[9], 'logo_file': record[10], 'admin_yn': record[11],
                   'in_date': record[12], 'in_user_id': record[13], 'up_date': record[14], 'up_user_id': record[15]}
        return obj

    def insert(self, owner_seq, owner_name, owner_id, owner_pwd, owner_str_name, owner_str_num, owner_str_tel, owner_add1, owner_add2, logo_path, logo_file):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        self.cs.execute(sql, (owner_seq, owner_name, owner_id, owner_pwd, owner_str_name, owner_str_num, owner_str_tel, owner_add1, owner_add2, logo_path, logo_file, owner_seq, owner_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def update(self, owner_name, owner_pwd, owner_str_name, owner_str_tel, owner_add1, owner_add2, logo_path, logo_file, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "update")
        self.cs.execute(sql, (owner_name, owner_pwd, owner_str_name, owner_str_tel, owner_add1, owner_add2, logo_path, logo_file, owner_seq, owner_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def update_pwd(self, owner_pwd, owner_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "update_pwd")
        self.cs.execute(sql, (owner_pwd, owner_id))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def delete(self, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete")
        self.cs.execute(sql, (owner_seq,))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def __del__(self):
        self.cs.close()
        self.conn.close()

    def id_check(self, owner_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "id_check")
        self.cs.execute(sql, (owner_id,))
        return self.cs.fetchone()[0]

    def owner_str_num_check(self, owner_str_num):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "owner_str_num_check")
        self.cs.execute(sql, (owner_str_num,))
        return self.cs.fetchone()[0]

    def id_check_list(self, owner_id, owner_str_num):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "id_check_list")
        record = self.cs.execute(sql, (owner_id, owner_str_num)).fetchone()
        return dict({'owner_seq': record[0], 'owner_name': record[1], 'owner_id': record[2], 'owner_pwd': record[3],
                     'owner_str_name': record[4], 'owner_str_num': record[5], 'owner_str_tel': record[6], 'owner_add1': record[7],
                     'owner_add2': record[8], 'logo_path': record[9], 'logo_file': record[10], 'admin_yn': record[11],
                     'in_date': record[12], 'in_user_id': record[13], 'up_date': record[14], 'up_user_id': record[15]})

    def daysChart(self, days):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "lastdays")
        rs = self.cs.execute(sql, (days,))
        list = []
        for record in rs:
            list.append({'tr_in_date': record[0], 'own_cnt': record[1]})
        return list

    def monthsChart(self, months):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "lastmonths")
        rs = self.cs.execute(sql, (months,))
        list = []
        for record in rs:
            list.append({'tr_in_date': record[0], 'own_cnt': record[1]})
        return list

if __name__ == '__main__':
    daoOwner = DaoOwner(config_path='../config.ini', xml_path='owner.xml')

#     list = dao.selectAll()
#     cnt = daoOwner.insert("3", "김현주", "khj@naver.com", "1234", "홍콩반점", "123434123", "01023121231", "12344", "대전 중구", "은행동", "", "", "y", "in_date", "khj", "", "khj")
#     cnt = dao.update("2", "3", "3","3","3","3","3","3","3","3","3","3","3","3")
#     cnt = dao.delete("2")
#     print(cnt)
#     list = daoOwner.dayschart(30)
#     print(list)
