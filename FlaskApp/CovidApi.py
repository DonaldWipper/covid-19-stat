import os
import requests
import json
import pandas as pd
from datetime import datetime
from datetime import timedelta
import time
import pycountry
from dateutil.relativedelta import relativedelta

# search country id by name
def get_id_country_name(name):
    try:
        return int(pycountry.countries.search_fuzzy(name)[0].numeric)
    except:
        return -1


# set random ids for new countries
def get_random_ids(number=0, list_old=[]):
    S = list_old
    S = [int(s) for s in S]
    res = []
    for cur_number in range(number):
        if len(S) > 0:
            if 0 not in S:
                S.append(0)
            number = next(iter(set(range(min(S) + 1, max(S))) - set(S)))
            S.append(number)
        else:
            number = -999
            S.append(number)
            S.append(0)
        res.append(number)
    return res


columns_rr1 = {"confirmed": "casetotal", "deaths": "deathcase", "recovered": "curecase"}

columns_rr2 = {
    "total_cases": "casetotal",
    "total_deaths": "deathcase",
    "total_recovered": "curecase",
    "new_cases": "newcase",
    "new_deaths": "newdeath",
}

country_replace = {
    "Korea, South": "Korea, Republic of",
    "S. Korea": "Korea, Republic of",
    "Congo (Brazzaville)": "Republic of the Congo",
    "Congo (Kinshasa)": "Congo, The Democratic Republic of the",
    "Taiwan*": "Taiwan",
    "Gambia, The": "Gambia",
    "Bahamas, The": "Bahamas",
    "Burma": "Myanmar",
    "S. Korea": "Korea, Republic of",
    "UAE": "United Arab Emirates",
    "Ivory Coast": "Côte d'Ivoire",
    "DRC": "Congo, The Democratic Republic of the",
    "Laos": "Lao People's Democratic Republic",
    "St. Vincent Grenadines": "Saint Vincent and the Grenadines",
}


class CovidApi:
    def __init__(self, settings, sql):
        self.settings = settings
        self.sql = sql
        self.headers = self.getHeaderRapid()
        self.countries_sql = sql.exec_query(
            "select * from {table}".format(
                table=self.settings["api"]["covid_api"]["countries_sql"]
            )
        )
        self.data_sql = sql.exec_query(
            "select * from {table}".format(
                table=self.settings["api"]["covid_api"]["data_sql"]
            )
        )
        self.data_sql  =  self.data_sql.fillna(0)
        self.dict_sql = dict(zip(self.countries_sql["name"], self.countries_sql["id"]))
        self.dict_sql_reverse = dict(
            zip(self.countries_sql["id"], self.countries_sql["name"])
        )
        self.columns = [
            column for column in self.data_sql.columns if column != "country"
        ] 

    def getHeaderRapid(self):
        self.headers = {
            "x-rapidapi-host": self.settings["api"]["covid_api"][
                "rapidapi_covid_monitor"
            ]["x-rapidapi-host"],
            "x-rapidapi-key": self.settings["api"]["covid_api"][
                "rapidapi_covid_monitor"
            ]["x-rapidapi-key"],
        }
        return self.headers

    def setCountryName(self, country_data):
        country_data["country"] = country_data.apply(
            lambda x: self.dict_sql_reverse[x["id_country"]], axis=1
        )
        return country_data

    def getWorldStat(self):
        url = self.settings["api"]["covid_api"]["rapidapi_covid_monitor"][
            "url_world_stat"
        ]
        res = requests.get(url, headers=self.headers).json()
        data = pd.DataFrame(data=res, index=[0])
        data = data.rename(columns=columns_rr2)
        for column in data.columns:
            try:
                data[column] = pd.to_numeric(data[column])
            except:
                try:
                    data[column] = pd.to_numeric(data[column].str.replace(",", ""))
                except:
                    data[column] = data[column]
        data.to_sql(
            self.settings["api"]["covid_api"]["world_data_sql"],
            con=self.sql.engine,
            index=False,
            if_exists="replace",
        )
        return data

    def GetStatAllCountry1(self):
        country_data = self.GetAffectedCountry1()
        countries = list(country_data["country"].drop_duplicates())
        url = self.settings["api"]["covid_api"]["github"]["url_all_countries_stat"]
        response = requests.request("GET", url, headers=self.headers).json()
        epidemic_country_data = pd.DataFrame()
        for country in countries:
            x = pd.DataFrame(data=response[country])
            x["country"] = country
            x = x.merge(country_data[["country", "id"]], how="left", on="country")
            epidemic_country_data = pd.concat([epidemic_country_data, x])

        epidemic_country_data.columns = [
            "day",
            "casetotal",
            "deathcase",
            "curecase",
            "country",
            "id_country",
        ]

        epidemic_country_data["activecase"] = (
            epidemic_country_data["casetotal"]
            - epidemic_country_data["curecase"]
            - epidemic_country_data["deathcase"]
        )
        epidemic_country_data["day"] = pd.to_datetime(
            epidemic_country_data["day"]
        ).dt.date
        epidemic_country_data["yesterday"] = epidemic_country_data[
            "day"
        ] + relativedelta(days=-1)

        epidemic_country_data = epidemic_country_data.merge(
            epidemic_country_data,
            how="left",
            left_on=["yesterday", "country"],
            right_on=["day", "country"],
            suffixes=("", "_yesterday"),
        )

        epidemic_country_data["id_country"] = epidemic_country_data[
            "id_country"
        ].fillna(-1)
        epidemic_country_data = epidemic_country_data.fillna(0)

        epidemic_country_data["newcase"] = (
            epidemic_country_data["casetotal"]
            - epidemic_country_data["casetotal_yesterday"]
        )
        epidemic_country_data["newcure"] = (
            epidemic_country_data["curecase"]
            - epidemic_country_data["curecase_yesterday"]
        )
        epidemic_country_data["newdeath"] = (
            epidemic_country_data["deathcase"]
            - epidemic_country_data["deathcase_yesterday"]
        )
        epidemic_country_data["newactive"] = (
            epidemic_country_data["activecase"]
            - epidemic_country_data["activecase_yesterday"]
        )
        epidemic_country_data = epidemic_country_data[self.columns]
        return epidemic_country_data

    def GetStatAllCountry2(self):
        res = pd.DataFrame()
        countries = self.GetAffectedCountry2()
        for country in list(countries["name"]):
            df = self.GetStatByCountry2(country)
            res = pd.concat([res, df])
        res = res.merge(
            countries[["name", "id"]],
            how="left",
            left_on="country_name",
            right_on="name",
        )
        columns_replace = {
            "total_cases": "casetotal",
            "total_deaths": "deathcase",
            "total_recovered": "curecase",
            "new_deaths": "new_death",
            "country_name": "country",
            "record_day": "day",
            "id": "id_country",
        }
        types = dict(res.dtypes)
        res = res.rename(columns=columns_replace)
        columns_numeric = ["casetotal", "deathcase", "curecase", "new_death"]
        for column in columns_numeric:
            try:
                res[column] = pd.to_numeric(res[column])
            except:
                res[column] = pd.to_numeric(res[column].str.replace(",", ""))
        
        res["activecase"] = res["casetotal"]- res["curecase"] - res["deathcase"]
        res["yesterday"] = res["day"] + relativedelta(days=-1)
        stat2 = res.merge(
            res,
            how="left",
            left_on=["id_country", "yesterday"],
            right_on=["id_country", "day"],
            suffixes=("", "_yesterday"),
        )
        stat2 = stat2.fillna(0).replace("", 0)
        stat2["newdeath"] = stat2["deathcase"] - stat2["deathcase_yesterday"]
        stat2["newcase"] = stat2["casetotal"] - stat2["casetotal_yesterday"]
        stat2["newcure"] = stat2["curecase"] - stat2["curecase_yesterday"]
        stat2["newactive"] = stat2["activecase"] - stat2["activecase_yesterday"]
        stat2 = stat2[self.columns]
        return stat2

    def GetStatByCountry2(self, country):
        url = self.settings["api"]["covid_api"]["rapidapi_covid_monitor"][
            "url_particular_country_stat"
        ]
        querystring = {"country": country}
        try:
            response = requests.request(
                "GET", url, headers=self.headers, params=querystring
            ).json()
        except:
            response = {}
        if "stat_by_country" in response.keys():
            result = pd.DataFrame(data=response["stat_by_country"])
        else:
            result = pd.DataFrame()
        if len(result) == 0:
            return result
        result["record_day"] = pd.to_datetime(result["record_date"]).dt.date
        result = (
            result.groupby(["country_name", "record_day"])
            .agg(
                {
                    "total_cases": "max",
                    "new_cases": "max",
                    "active_cases": "max",
                    "total_deaths": "max",
                    "new_deaths": "max",
                    "total_recovered": "max",
                    "serious_critical": "max",
                    "record_date": "max",
                }
            )
            .reset_index()
        )
        return result

    def saveNewCountries(self, country_data_new):
        S = list(self.countries_sql[self.countries_sql["id"] < 0]["id"])
        ids = get_random_ids(len(country_data_new), S)
        country_data_new["id"] = ids
        country_data_new.columns = ["name", "name_new", "id"]
        country_data_new[["name", "id"]].to_sql(
            self.settings["api"]["covid_api"]["countries_sql"],
            con=self.sql.engine,
            index=False,
            if_exists="append",
        )

    def reinitCountriesSQL(self):
        self.data_sql = self.sql.exec_query(
            "select * from {table}".format(
                table=self.settings["api"]["covid_api"]["data_sql"]
            )
        )
        self.dict_sql = dict(zip(self.countries_sql["name"], self.countries_sql["id"]))

    def GetAffectedCountry1(self):
        url = self.settings["api"]["covid_api"]["github"]["url_all_countries_stat"]
        response = requests.request("GET", url, headers=self.headers).json()
        country_data = pd.DataFrame(data=list(response.keys()))
        country_data.columns = ["country"]
        country_data["country_new"] = country_data["country"].replace(country_replace)
        country_data["id"] = country_data.apply(
            lambda x: get_id_country_name(x["country_new"]), axis=1
        )
        country_data["id"] = country_data.apply(
            lambda x: self.dict_sql[x["country"]]
            if x["id"] == -1 and x["country"] in self.dict_sql
            else x["id"],
            axis=1,
        )
        country_data_new = country_data[country_data["id"] == -1].drop_duplicates()
        if len(country_data_new) > 0:
            self.saveNewCountries(country_data_new)
            self.reinitCountriesSQL()
            country_data["id"] = country_data.apply(
                lambda x: self.dict_sql[x["country"]]
                if x["id"] == -1 and x["country"] in self.dict_sql
                else x["id"],
                axis=1,
            )
        return country_data

    # save new data
    def mergeWithOld(self, epidemic_country_data):
        self.data_sql = self.data_sql[self.columns].drop_duplicates()
        self.data_sql.to_sql(
            self.settings["api"]["covid_api"]["data_sql"] + "_old",
            con=self.sql.engine,
            index=False,
            if_exists="replace",
        )
        stats_new = epidemic_country_data.set_index(["day", "id_country"])
        stats_old = self.data_sql.set_index(["day", "id_country"])
        take_bigger =  lambda s1, s2: s1 if s1.sum() >= s2.sum() else s2
        x = stats_new.combine(stats_old, take_bigger)
        x = x.reset_index()
        res = self.setCountryName(x)
        res = res.fillna(0)
        res = res[res["casetotal"] > 0].drop_duplicates()
        res.to_sql(
            self.settings["api"]["covid_api"]["data_sql"],
            con=self.sql.engine,
            index=False,
            if_exists="replace",
        )
        return res

    # получаем токен первый раз
    def GetAffectedCountry2(self):
        url = self.settings["api"]["covid_api"]["rapidapi_covid_monitor"][
            "url_affected_countries"
        ]
        response = requests.request("GET", url, headers=self.headers).json()
        result = pd.DataFrame(data=response["affected_countries"])
        result = result.replace(country_replace)
        result.columns = ["name"]
        result["id"] = result.apply(lambda x: get_id_country_name(x["name"]), axis=1)
        result["id"] = result.apply(
            lambda x: self.dict_sql[x["name"]]
            if x["id"] == -1 and x["name"] in self.dict_sql
            else x["id"],
            axis=1,
        )
        result = result.merge(
            self.countries_sql, how="left", on="id", suffixes=("", "_new")
        )
        country_data_new = result[result["id"] == -1][
            ["name", "name_new", "id"]
        ].drop_duplicates()
        if len(country_data_new) > 0:
            self.saveNewCountries(country_data_new)
            self.reinitCountriesSQL()
            result["id"] = result.apply(
                lambda x: self.dict_sql[x["name"]]
                if x["id"] == -1 and x["name"] in self.dict_sql
                else x["id"],
                axis=1,
            )
        return result