import json
import requests
import jinja2
from flask import Flask, render_template,request
from wtforms import Form, RadioField,validators

from autoCompleteBenchmarking import *

app = Flask(__name__)

@app.route("/information")
def info():
    return "<h1> Search keyword comparision<h1>"

@app.route("/",methods=['GET','POST'])
def compare():
    results = getDataFromResults()
    print("number of keywords are {}".format(len(results)))
    return render_template('compare.html',results=results)

#def extractLatLons():
if __name__ == '__main__':
         app.run(debug = True)
