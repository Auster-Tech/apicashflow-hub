from typing import Any, List, Optional, Tuple, Dict, TypeVar
from models import Status
from pymysql.connections import Connection


class Query:
    def __init__(self, table: str, connection: Connection, **fieldsFilter):
        self.table = table
        self.connection = connection
        self._where = dict()
        self._where_flag = False

        if len(fieldsFilter) > 0:
            self._where = fieldsFilter
            self._where_flag = True
    
    def find(self, first:bool = False):
        result = []
        with self.connection.cursor() as cursor:
            sql = F"SELECT * FROM `{self.table}`"
            
            if self._where_flag:
                sql += f" WHERE " +\
                    " AND ".join([f"{key} = %({key})s" for key in self._where.keys()])
            
            cursor.execute(sql, self._where)
            if first:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()

        return result
    
    def create(self):
        if not self._where_flag:
            raise Exception("No data specified to be inserted")
        
        client_data = self._where
        columns = client_data.keys()
        col_list_str = "`,`".join(columns)
        
        values_list = [f"%({column})s" for column in columns]
        values_list_str = ", ".join(values_list)

        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `{self.table}` (`{col_list_str}`) VALUES ({values_list_str})"
            cursor.execute(sql, client_data)

        self.connection.commit()

    def update(self):
        if not self._where_flag:
            raise Exception("No data specified to be udpated")
        
        client_data = self._where

        if 'id' not in client_data:
            raise Exception("Id must be specified in update")
        
        id = client_data.pop('id')
        set_values = []
        
        for column in client_data.keys():
            set_values.append(f"{column} = %({column})s")
        
        set_clause = ", ".join(set_values)
        
        with self.connection.cursor() as cursor:
            sql = f"UPDATE `{self.table}` SET {set_clause} WHERE `id` = {id}"

            cursor.execute(sql, client_data)

        self.connection.commit()

    def delete(self):
        if not self._where_flag:
            raise Exception("No data specified to be deleted")

        if 'id' not in self._where:
            raise Exception("Id must be specified in delete")
    
        record_id = self._where['id']
        with self.connection.cursor() as cursor:
            sql = f"UPDATE `{self.table}` SET status = %s WHERE id = %s"
            cursor.execute(sql, (Status.DELETED.value, record_id))
        self.connection.commit()
