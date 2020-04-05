import requests
import pandas as pd
import numpy as np
from environs import Env
import FlaskApp.SQL as SQL
import FlaskApp.CovidApi as CovidApi
import json

env = Env()
env.read_env()
def read_params(fn):
    d = {}
    with open(fn, "r", encoding="utf-8") as file:
        d = json.load(file)

    return d

try:
    settings = read_params("credentials.json")
except:
    settings = read_params("FlaskApp/credentials.json")
    
def run():
    sql = SQL.SQLWorker(env.str("DB_CONN_STR"))
    covid_api = CovidApi.CovidApi(settings, sql)
    covid_api.getWorldStat()
    stat1 = covid_api.GetStatAllCountry1()
    stat1 = stat1.fillna(0)
    covid_api.mergeWithOld(stat1)
    
run()    