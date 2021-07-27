import cx_Oracle
import mybatis_mapper2sql
import configparser


def menusort(menuList : list):
    return {'sys_ques_seq': menuList[0], 
            'sys_ans_reply': menuList[1], 
            'in_date': menuList[2], 
            'in_user_id': menuList[3], 
            'up_date': menuList[4], 
            'up_user_id': menuList[5]}

class DaoSysAns:
    def __init__(self, config_path='config.ini', xml_path='dao/sys_ans.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]

    def select(self, sys_ques_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        #         MyLog().getLogger().debug(sql)
        rs = self.cs.execute(sql, (sys_ques_seq,))
        
        list = rs.fetchone()
        if list :
            return menusort(list)
        return list

    def insert(self, sys_ques_seq, sys_ans_reply, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        #         mylog().getlogger().debug(sql)
        self.cs.execute(sql, (sys_ques_seq, sys_ans_reply, in_user_id, up_user_id))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def delete(self, sys_ques_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete")
        #         mylog().getlogger().debug(sql)
        self.cs.execute(sql, (sys_ques_seq,))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

if __name__ == '__main__':
    dao = DaoSysAns(config_path='../config.ini', xml_path='sys_ans.xml')
#     dao.select("1")
#     print(cnt)
