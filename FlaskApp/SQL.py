from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps
import pandas as pd

# secrets.py contains credentials, etc.


class SQLWorker():
    def __init__(self, settings, db = "datarig", ssh = True, type_sql = "postgre"):
        self.settings = settings
        self.db = db
        if type_sql == "postgre":
            self.sql_name_str = "postgresql"
        elif type_sql == "mysql":
            self.sql_name_str = "mysql"
        else:
            self.sql_name_str = "postgresql"
        #mysql+mysqldb
        self.url_engine = ""
        self.tunnel = None
        self.engine = None
        self.connection = None
        #запуск туннеля
        if self.tunnel == None and ssh == True:
            self.__up_ssh_tunnel()
        #создание подключения к db
        if ssh == True:
            self.engine = self.__get_engine_for_port(self.tunnel.local_bind_port)
            #self.engine = self.__get_engine_for_port(5432)
           
        else:
            self.engine = self.__get_engine_for_port_no_ssh()

    def __del__(self):
        if self.tunnel != None:
            self.tunnel.close()
        if self.connection != None:   
            self.connection.close()

    def __up_ssh_tunnel(self):
        #print(self.settings["databases"]["ssh_tonnel"]["ssh_private_key_path"])
        self.tunnel = SSHTunnelForwarder(
            (
                self.settings["databases"]["ssh_tonnel"]["ip"],
                int(self.settings["databases"]["ssh_tonnel"]["port"]),
            ),
            ssh_username=self.settings["databases"]["ssh_tonnel"]["login"],
            ssh_pkey=self.settings["databases"]["ssh_tonnel"]["ssh_private_key_path"],
            ssh_private_key_password="",
            remote_bind_address=(
                self.settings["databases"][self.db]["ip"],
                int(self.settings["databases"][self.db]["port"]),
            ),
        )
        self.tunnel.start()

    def exec_query(self, query):
        
        if self.connection == None:
            self.connection = self.engine.connect()
        
        #result = self.connection.execute(query)
        df = pd.read_sql_query(query, self.engine)
        self.connection.close()
        return df

    def __get_engine_for_port(self, port):
        self.url_engine = "{type_sql}://{user}:{password}@{host}:{port}/{db}".format(
                type_sql = self.sql_name_str,
                user=self.settings["databases"][self.db]["login"],
                password=self.settings["databases"][self.db]["password"],
                host="localhost",
                port=port,
                db=self.settings["databases"][self.db]["db"],
            )
        #print(self.url_engine)
        return create_engine(self.url_engine)
    
    def __get_engine_for_port_no_ssh(self):
        self.url_engine =  "{type_sql}://{user}:{password}@{host}:{port}/{db}".format(
                type_sql = self.sql_name_str,
                user=self.settings["databases"][self.db]["login"],
                password=self.settings["databases"][self.db]["password"],
                host=self.settings["databases"][self.db]["ip"],
                port=int(self.settings["databases"][self.db]["port"]),
                db=self.settings["databases"][self.db]["db"],
            )
        return create_engine(self.url_engine)