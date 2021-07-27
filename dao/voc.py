import cx_Oracle
import mybatis_mapper2sql
import configparser


def vocSort(vocList: list):
    if vocList:
        return {"voc_seq": vocList[0],
                "owner_seq": vocList[1],
                "content": vocList[2],
                "in_date": vocList[3],
                "in_user_id": vocList[4],
                "up_date": vocList[5],
                "up_user_id": vocList[6]}
    else:
        return None


class DaoVoc:
    def __init__(self, config_path='config.ini', xml_path='dao/voc.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]

    def select(self, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        rs = self.cs.execute(sql, (owner_seq,))
        list = []
        for record in rs:
            list.append({'voc_seq': record[0], 'owner_seq': record[1], 'content': record[2]
                            , 'in_date': record[3], 'in_user_id': record[4], 'up_date': record[5], 'up_user_id': record[6]})
        return list

    def insert(self, owner_seq, content, in_user_id, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        self.cs.execute(sql, (owner_seq, content, owner_seq, owner_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt


if __name__ == '__main__':
    dao = DaoVoc(config_path='../config.ini', xml_path='voc.xml')
