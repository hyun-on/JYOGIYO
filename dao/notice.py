import cx_Oracle
import mybatis_mapper2sql
import configparser

class DaoNotice:
    def __init__(self, config_path='config.ini', xml_path='dao/notice.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]


    def selectlist(self):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "selectAll")
        rs = self.cs.execute(sql)
        list=[]
        for record in rs:
            list.append({'noti_seq':record[0],'noti_title':record[1],'noti_content':record[2],'attach_path':record[3],
                         'attach_file':record[4],'in_date':record[5],'in_user_id':record[6],'up_date':record[7],'up_user_id':record[8]})
        return list
    
    def select(self, noti_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        rs = self.cs.execute(sql,(noti_seq,))
        obj = None
        for record in rs:
            obj = {'noti_seq':record[0],'noti_title':record[1],'noti_content':record[2],'attach_path':record[3],
                    'attach_file':record[4],'in_date':record[5],'in_user_id':record[6],'up_date':record[7],'up_user_id':record[8]}
        return obj
    
    def insert(self, noti_title, noti_content, attach_path, attach_file, owner_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        self.cs.execute(sql, (noti_title, noti_content, attach_path, attach_file, owner_id, owner_id))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    
    def update(self, noti_seq, noti_title, noti_content, attach_path, attach_file, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "update")        
        self.cs.execute(sql, (noti_title, noti_content, attach_path, attach_file,up_user_id, noti_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt
    

    def del_img(self, noti_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "del_img")
        self.cs.execute(sql, (noti_seq,))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt
        pass
    
    def delete(self , noti_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete")        
        self.cs.execute(sql,( noti_seq,))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def __del__(self):
        self.cs.close()
        self.conn.close()
    
        
if __name__ == '__main__':
    dao = DaoNotice(config_path='../config.ini', xml_path='notice.xml')
#     cnt = dao.insert("noti_title", "noti_content", "attach_path", "attach_file", "owner_id")
#     cnt = dao.update("1", "noti", "noti","y","in_date","in_user_id","up_date","up_user_id")
#     cnt = dao.delete("1")
#     print(cnt)
