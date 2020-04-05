import requests
import pandas as pd
import numpy as np
import SQL as SQL
import CovidApi
import json


def read_params(fn):
    d = {}
    with open(fn, "r", encoding="utf-8") as file:
        d = json.load(file)

    return d

settings = read_params("credentials.json")
def run():
    sql = SQL.SQLWorker(settings, db="mysql", type_sql="mysql", ssh=False)
    covid_api = CovidApi.CovidApi(settings, sql)
    covid_api.getWorldStat()
    stat1 = covid_api.GetStatAllCountry1()
    stat1 = stat1.fillna(0)
    covid_api.mergeWithOld(stat1)
    
run()    