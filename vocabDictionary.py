import requests
import json 
from pprint import pprint
from urllib.request import urlopen
import re
import os 
import glob
from PyDictionary import PyDictionary

dictionary=PyDictionary()

print (dictionary.meaning("front-desk"))
print (dictionary.synonym("entertainment"))


def update_defs():
    with open('new_audio.txt', 'r') as json_file:
        masterDict = json.load(json_file)    
        
    for vocab in masterDict: 
        pass       
        

    with open('new_defs.txt', 'w') as json_file:
        json.dump(masterDict, json_file)

    return True

#action = update_defs()


