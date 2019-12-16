import sys, boto3, random
import datetime
import ast
import json
from random import randint
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import LoginForm
from pprint import pprint
from models import *
from flask_socketio import SocketIO, join_room, leave_room, send, emit
try:
    from config import AWS
    s3_resource = AWS.s3_resource
except:
    s3_resource = boto3.resource('s3')

    

@app.route("/listoptions", methods=['GET','POST'])
def listOptions():
    with open('vocab1.txt', 'r') as json_file:
        vocabList = json.load(json_file)
    
    allItems = len(vocabList)

    counter = 0

    listicle = {
        'all' : 'All items', 
        'pro' : 'Proper Nouns', 
        'two' : 'Phrase (2 words)', 
        'thr' : 'Phrases (3+ words)',         
        'lng' : 'Detailed Definitions', 
        'mdf' : 'Multiple Definitions'   
    }


    return render_template('listMenu.html', title='Vocab', listicle=listicle)

@app.route("/listrandoms", methods=['GET','POST'])
def listRandoms():
    with open('vocab1.txt', 'r') as json_file:
        vocabList = json.load(json_file)
    
    allItems = len(vocabList)

    listicle = {
        'all' : 'All items', 
        'pro' : 'Proper Nouns', 
        'two' : 'Phrase (2 words)', 
        'thr' : 'Phrases (3+ words)',         
        'lng' : 'Detailed Definitions', 
        'mdf' : 'Multiple Definitions'   
    }

    return render_template('listTest.html', title='Vocab', listicle=listicle)


@app.route("/list/<string:filt>", methods=['GET','POST'])
def vocabSorter(filt):

    # type  all, acr, pro, two, mlt, 

    with open('vocab1.txt', 'r') as json_file:
        vocabList = json.load(json_file)
    
    search = {
        'acr' : 'Acronym', 
        'pro' : 'Proper', 
        'two' : 'Double', 
        'thr' : 'Multiple',         
        'lng' : 'longdef', 
        'mdf' : 'multidef'        
    }

    if filt == 'all':
        typeDict = vocabList
    else:
        typeDict = {}
        for vocab in vocabList:
            if search[filt] in vocabList[vocab]['tags']:
                typeDict[vocab] = vocabList[vocab]


    
    return render_template('listVocab.html', title='Vocab', vocabList=typeDict)



def loadJson():
    s3_resource = AWS.s3_resource
    file_name = 'jfolder/' + current_user.username + '.json'
    content_object = s3_resource.Object('lms-tester', file_name)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    jload = json.loads(file_content)
    return jload

def putJson(updateDict):
    s3_resource = AWS.s3_resource
    file_name = 'jfolder/' + current_user.username + '.json'    
    jstring = json.dumps(updateDict)
    s3_resource.Bucket('lms-tester').put_object(Key=file_name, Body=jstring)
    return jstring

@app.route('/update', methods=['POST', 'GET'])
def vocabUpdate():

    state = request.form ['state']
    vocab = request.form ['vocab'] 
    time = datetime.now()

    updateDict = loadJson()

    if vocab in updateDict:
        updateDict[vocab]['state'] = state
        updateDict[vocab]['time'] = str(time)
        updateDict[vocab]['check'] += 1   
    else: 
        updateDict[vocab] = {}
        updateDict[vocab]['state'] = state
        updateDict[vocab]['time'] = str(time)
        updateDict[vocab]['check'] = 1    

    pprint (putJson(updateDict))  

    return jsonify({'state' : state,  'time' : str(time), 'vocab' : vocab})    
    


@app.route("/random/<int:rand>/<int:count>", methods=['GET','POST'])
def vocabRandom(rand, count):

    # 1 random 
    # 2 random unmarked
    # 3 random marked hard
    # 4 random makred medium 
    # 5 random marked easy
    # 6 random marked general
    
    with open('vocab1.txt', 'r') as json_file:
        vocabList = json.load(json_file)

    randList = {}
    while len (randList) < count:
        random_vocab = random.choice(list(vocabList.keys()))
        if random_vocab in randList:
            pass
        else: 
            randList[random_vocab] = vocabList[random_vocab]
    
    
    
    return render_template('listRandom.html', title='Random', vocabList=vocabList, randList=randList)