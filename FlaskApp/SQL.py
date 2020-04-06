from sqlalchemy import create_engine
import pandas as pd

# secrets.py contains credentials, etc.


class SQLWorker():
    def __init__(self, db_string):
        self.engine = db_string
        self.engine = self.__get_engine_for_port_no_ssh()

    def exec_query(self, query):
        self.connection = self.engine.connect()
        df = pd.read_sql_query(query, self.engine)
        self.connection.close()
        return df


    
    def __get_engine_for_port_no_ssh(self):
        return create_engine(self.engine)