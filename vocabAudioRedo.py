from bs4 import BeautifulSoup
import requests
import json 
from pprint import pprint
from urllib.request import urlopen
import re
from gtts import gTTS   
import os 
import glob




def update_audio():
    with open('master.txt', 'r') as json_file:
        masterDict = json.load(json_file)    
        
    for vocab in masterDict:        
        if 'amazon' in str(masterDict[vocab]['Audio']): 
            masterDict[vocab]['Audio'] = masterDict[vocab]['Audio'][0] 
        else:
            string = vocab + '.mp3'
            save = "static/audio/" + string  
            find = "static/audio\\" + string
            s3 = "https://lms-tester.s3-ap-northeast-1.amazonaws.com/audio_en/" + string
            audio_files = glob.glob("static/audio/*.mp3")   
            if find in audio_files:
                masterDict[vocab]['Audio'] = s3
                print('PASS', vocab)
            else:           
                vocab_audiofile = gTTS(text=vocab, lang='en', slow=False)                         
                vocab_audiofile.save(save)
                masterDict[vocab]['Audio'] = s3
                print ('MP3', vocab)

    with open('new_audio.txt', 'w') as json_file:
        json.dump(masterDict, json_file)

    return True

action = update_audio()


