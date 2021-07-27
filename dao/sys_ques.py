import cx_Oracle
import mybatis_mapper2sql
import configparser


def menusort(munuList: list):
    return {'sys_ques_seq': munuList[0],
            'owner_seq': munuList[1],
            'sys_ques_title': munuList[2],
            'sys_ques_content': munuList[3],
            'sys_ques_display_yn': munuList[4],
            'attach_path': munuList[5],
            'attach_file': munuList[6],
            'in_date': munuList[7],
            'in_user_id': munuList[8],
            'up_date': munuList[9],
            'up_user_id': munuList[10],
            'reply_in_date': munuList[11]}


class DaoSysQues:
    def __init__(self, config_path='config.ini', xml_path='dao/sys_ques.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]

    def selectAll(self, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "selectAll")
        #         MyLog().getLogger().debug(sql)
        rs = self.cs.execute(sql, (owner_seq,))
        return list(map(menusort, rs.fetchall()))

    def select(self, sys_ques_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        #         MyLog().getLogger().debug(sql)
        rs = self.cs.execute(sql, (sys_ques_seq,))
        return menusort(rs.fetchone())

    def insert(self, owner_seq, sys_ques_title, sys_ques_content, sys_ques_display_yn, attach_path, attach_file, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        #         mylog().getlogger().debug(sql)
        self.cs.execute(sql, (owner_seq, sys_ques_title, sys_ques_content, sys_ques_display_yn, attach_path, attach_file, owner_seq, owner_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def update(self, sys_ques_seq, sys_ques_title, sys_ques_content, sys_ques_display_yn, attach_path, attach_file, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "update")
        #         mylog().getlogger().debug(sql)
        self.cs.execute(sql, (sys_ques_title, sys_ques_content, sys_ques_display_yn, attach_path, attach_file, sys_ques_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def delete_img(self, sys_ques_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete_img")
        #         MyLog().getLogger().debug(sql)
        self.cs.execute(sql, ('', '', sys_ques_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        print(cnt)
        return cnt

    def delete(self, sys_ques_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete")
        #         mylog().getlogger().debug(sql)
        self.cs.execute(sql, (sys_ques_seq,))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt


if __name__ == '__main__':
    dao = DaoSysQues(config_path='../config.ini', xml_path='sys_ques.xml')
    dao.selectAll(22)

#     cnt = dao.insert("1", "카테고리 내의 메뉴 한번에 못 지우나요?", "카테고리 내의 메뉴 한번에 못 지우나요?카테고리 내의 메뉴 한번에 못 지우나요?", "y", "", "", "", "abc@naver.com", "", "abc@naver.com")
#     cnt = dao.insert("1", "힘들어요 살려주세요?", "카테고리 내의 메뉴 한번에 못 지우나요?카테고리 내의 메뉴 한번에 못 지우나요?", "y",  "", "", "", "abc@naver.com", "", "abc@naver.com")
#     cnt = dao.insert("1", "비용은 얼마에요?", "카테고리 내의 메뉴 한번에 못 지우나요?카테고리 내의 메뉴 한번에 못 지우나요?", "y",  "", "", "", "abc@naver.com", "", "abc@naver.com")
#     print(cnt)
