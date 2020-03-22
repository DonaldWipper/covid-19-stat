from flask import Flask, render_template, make_response
#from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
try:
    import FlaskApp.sql
except:
    import sql
from environs import Env
from flask import request, flash
import json
import requests
import csv
from datetime import date
from datetime import datetime
import os
from cubes.server.base import create_server
from cubes.server.base import read_slicer_config
from cubes.server.utils import str_to_bool
from cubes.server.blueprint import slicer
import io
import configparser
# Set the configuration file
try:
    CONFIG_PATH = os.environ["SLICER_CONFIG"]
except KeyError:
    CONFIG_PATH = os.path.join(os.getcwd(), "slicer.ini")

#счатаем параметр в
def create_server_(config=None, **_options):
    # Load extensions
    if config.has_option("server", "modules"):
        modules = shlex.split(config.get("server", "modules"))
        for module in modules:
            e = __import__(module)

    app = Flask(__name__.rsplit('.', 1)[0])
    app.register_blueprint(slicer, config=config, url_prefix='/api', **_options)
    return app    

def read_config_local(config_path):
    env = Env()
    # Read .env into os.environ
    env.read_env()
    fin = open(config_path, "r")
    x = fin.read().format(DB_CONN_STR =env.str("DB_CONN_STR")) 
    fin.close()
    buf = io.StringIO(x)
    config = configparser.ConfigParser()
    config.read_file(buf)
    return config


    
#app.config.from_object(__name__)
#config = read_slicer_config(CONFIG_PATH)
config = read_config_local(CONFIG_PATH)                          
app = create_server_(config)
app.config['TEMPLATES_AUTO_RELOAD']=True
debug = os.environ.get("SLICER_DEBUG")




@app.route("/", methods=['GET'])
def main():
    return render_template("studio.html")
    

if __name__ == "__main__":
    if debug and str_to_bool(debug):
        app.debug = True
    app.run()

