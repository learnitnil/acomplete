import os,sys
import requests
import json

#flask imports
import jinja2
from flask import Flask, render_template,request
from wtforms import Form, RadioField,validators


G_URL="https://maps.googleapis.com/maps/api/place/autocomplete/json?"
G_KEY = REPLACE WITH GOOGLE KEY

#Here url and credentials
H_URL="http://autocomplete.geocoder.api.here.com/6.2/suggest.json"
H_APP_ID = "XyifzbyPyVEWTOQF4tDK"
H_APP_CODE = "s2N9-uw08-1zQe06blQYtg"

R_URL="http://67.227.142.20:4000/v1/autocomplete"

SEPERATOR = '@'

#keywords source file name
KEYWORD_SOURCE = "keywords.txt"

def saveToTextFile(data,keyword,tech) :
  """
  data : data returned from get request
  tech : here / google / osm / pilot
  """
  fileName = keyword + '.json'
  folderToAdd = os.path.join(tech,fileName)
  print("filename is {0}".format(fileName))
  locationToSaveFile = folderToAdd
  #convert data into json
  with open(locationToSaveFile, 'w') as f:
    json.dump(data, f)

def getTechArray() :
  return ["remoteServer","hereServer","googleServer"]

#create dir if it doesn't exist
def checkAndCreateDirectories(DirNames):
        for dirName in DirNames:
            if os.path.isdir(dirName):
               print("{0} already exist".format(dirName))
            else:
                  os.mkdir(dirName)
                  print("{0} is created ".format(dirName))


def readKeywordsFromFile():
  try:
    f = open(KEYWORD_SOURCE, "r")
  except FileNotFoundError:
    print("unable to open {0} file missing ".format(KEYWORD_SOURCE))
    sys.exit()
  keywordList = list()
  for line in f:
    #remove leading and trailing white spaces
    line = line.strip()
    # add the places to the places list
    keywordList.append(line)
  #print(placesList)
  print("number of keywrods are {}".format(len(keywordList)))
  return keywordList


def getKeywordInfo(keyword,tech) :
    if tech == 'googleServer' :
        print("got google server")
        params = {'input': keyword,
                    "key": G_KEY,
                    "location":'24.466667,54.366669',
                    "radius" : 1000000
        }
        URL = G_URL
    elif tech == 'hereServer' :
        print("got here server")
        params = {'query': keyword,
                  "app_id": H_APP_ID,
                  "app_code": H_APP_CODE,
                  "country" : "ARE"
                  }
        URL = H_URL
    elif tech == 'remoteServer' :
        print("got remote server")
        URL = R_URL
        params = {
            "text" : keyword
        }
    r = requests.get(url=URL, params=params, timeout=10)
    print(r.url)
    data = r.json()
    #add server response time to the result
    roundTrip = r.elapsed.total_seconds()
    data["time"] = roundTrip
    return data


def downloadKeywordInfo():
    checkAndCreateDirectories(DirNames)
    keywordList = readKeywordsFromFile()
    techArray = getTechArray()
    for keyword in keywordList :
        for tech in techArray :
            data = getKeywordInfo(keyword,tech)
            saveToTextFile(data,keyword,tech)

def processJSONFiles(keyword,tech):
    fileToRead = os.path.join(tech,keyword+'.json')
    fHandler = open(fileToRead)
    data = json.load(fHandler)
    fHandler.close()
    out = list()
    if tech == 'hereServer' :
        suggestionList = data['suggestions']
        for suggestion in suggestionList :
            out.append(suggestion['label'])
    elif tech == 'remoteServer' :
        suggestionList = data['features']
        for suggestion in suggestionList :
            out.append(suggestion['properties']['label'])
    elif tech == 'googleServer' :
        suggestionList = data['predictions']
        for suggestion in suggestionList :
            out.append(suggestion['description'])
    return out

def getDataFromResults():
    resultsFile = os.path.join('results/results.csv')
    fHandler = open(resultsFile)
    allLines = list()
    for line in fHandler :
        allLines.append(line)
    #ignore first first lines - since it contains metadata
    data = allLines[1:]
    return data

def processKeywordInfo():
  keywordList = readKeywordsFromFile()
  techArray = getTechArray()
  #open file to write response
  fileToSave = os.path.join('results','results.csv')
  fHandler = open(fileToSave,'w')

  #write meta data for csv file
  strToWrite = 'keyword,'
  for tech in techArray :
      strToWrite = strToWrite+tech+SEPERATOR
  fHandler.write(strToWrite+'\n')

  #process data from
  for keyword in keywordList :
    dataToWrite = []
    for tech in techArray:
      result = processJSONFiles(keyword,tech)
      print("{0} -- {1}".format(tech,result))
      dataToWrite.append(','.join(result))
      dataToWrite.append(SEPERATOR)
    fHandler.write(keyword + '@' +','.join(dataToWrite)+'\n')
    print("completed processing for {0}".format(keyword))

###############################################
########## LOGIC STARTS FROM HERE #############
###############################################
if __name__ == "__main__" :
  #last one should be results
  DirNames = ['remoteServer', 'hereServer', 'googleServer', 'results']
  techArray = getTechArray()
  #action - download , process, graph, all
  action = 'all'
  if action == 'download' :
      downloadKeywordInfo()
  elif action == 'process' :
      processKeywordInfo()
  elif action == 'all' :
      downloadKeywordInfo()
      processKeywordInfo()
