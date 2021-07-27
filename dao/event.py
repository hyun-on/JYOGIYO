import cx_Oracle
import mybatis_mapper2sql
import configparser


class DaoEvent:
    def __init__(self, config_path='config.ini', xml_path='dao/event.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]

    def selectAll(self, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "selectAll")
        rs = self.cs.execute(sql, (owner_seq,))
        list = []
        for record in rs:
            list.append({'owner_seq': record[0], 'event_seq': record[1], 'event_title': record[2], 'event_content': record[3]
                            , 'event_start': record[4], 'event_end': record[5], 'attach_path': record[6], 'attach_file': record[7]
                            , 'in_date': record[8], 'in_user_id': record[9], 'up_date': record[10], 'up_user_id': record[11]})
        return list

    def select(self, owner_seq, event_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        rs = self.cs.execute(sql, (event_seq, owner_seq))
        obj = None
        for record in rs:
            obj = {'owner_seq': record[0], 'event_seq': record[1], 'event_title': record[2], 'event_content': record[3]
                , 'event_start': record[4], 'event_end': record[5], 'attach_path': record[6], 'attach_file': record[7]
                , 'in_date': record[8], 'in_user_id': record[9], 'up_date': record[10], 'up_user_id': record[11]}
        return obj

    def insert(self, owner_seq, event_seq, event_title, event_content, event_start, event_end, attach_path, attach_file, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        self.cs.execute(sql, (owner_seq, event_title, event_content, event_start, event_end, attach_path, attach_file, in_user_id, up_user_id))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def update(self, owner_seq, event_seq, event_title, event_content, event_start, event_end, attach_path, attach_file, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "update")
        self.cs.execute(sql, (event_title, event_content, event_start, event_end, attach_path, attach_file, owner_seq, event_seq, owner_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def del_img(self, owner_seq, event_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "del_img")
        self.cs.execute(sql, (owner_seq, event_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def delete(self, owner_seq, event_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete")
        self.cs.execute(sql, (owner_seq, event_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def __del__(self):
        self.cs.close()
        self.conn.close()


if __name__ == '__main__':
    daoEvent = DaoEvent(config_path='../config.ini', xml_path='event.xml')
    # cnt = daoEvent.insert('1', '2', '1', '1', '20210408', '20210409', '1','1','1', '1', '1', '1')
    # cnt = daoEvent.update('1', '1', '1', '61', '20210408', '20210409', '1','2','1', '1', '1', '41')
    # cnt = daoEvent.delete('1','41')
    # print(cnt)
