import sys, boto3, random
import datetime
import ast
import time
import datetime
from datetime import timedelta
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

def loadMaster():
    file_name = 'jfolder/' + 'master' + '.txt'
    content_object = s3_resource.Object('lms-tester', file_name)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    with open('vocab1.txt', 'r') as json_file:
        jMaster = json.load(json_file)    
    return jMaster    

@app.route("/listoptions", methods=['GET','POST'])
@login_required 
def listOptions():   

    categ = {
        'all' : 'All items', 
        'pro' : 'Proper Nouns', 
        'two' : 'Phrase (2 words)', 
        'thr' : 'Phrases (3+ words)',         
        'lng' : 'Detailed Definitions', 
        'mdf' : 'Multiple Definitions'   
    }

    alphabet ='abcdefghijklmnopqrstuvwxyz'

    states = {
        '1' : 'Hard',
        '2' : 'Unsure',
        '3' : 'Easy'
    }

    times = {
        'ys' : 'yesterday',
        'wk' : 'last week', 
        'mn' : 'last month'
    }

    return render_template('listMenu.html', title='Vocab', alphabet=alphabet, times=times, states=states, categ=categ )

@app.route("/listrandoms", methods=['GET','POST'])
@login_required 
def listRandoms():
    
    vocabList = loadMaster()
    
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


def loadJson():
    file_name = (User.query.filter_by(id=current_user.id).first().j_location).split('com/')[1]
    print (file_name)
    content_object = s3_resource.Object('lms-tester', file_name)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    jload = json.loads(file_content)
    return jload

def putJson(updateDict):
    file_name = (User.query.filter_by(id=current_user.id).first().j_location).split('com/')[1]
    jstring = json.dumps(updateDict)
    s3_resource.Bucket('lms-tester').put_object(Key=file_name, Body=jstring)
    return jstring


@app.route("/list/<string:filt>", methods=['GET','POST'])
@login_required 
def vocabSorter(filt): 
    vocabList = loadMaster()    
    student_vocab = loadJson()

    search = {
        'acr' : 'Acronym', 
        'pro' : 'Proper', 
        'two' : 'Double', 
        'thr' : 'Multiple',         
        'lng' : 'longdef', 
        'mdf' : 'multidef'        
    }
    
    states = {
        '1' : 'Hard',
        '2' : 'Unsure',
        '3' : 'Easy'
    }

    typeDict = {}

    try:
        int(filt)
        integer = True
    except:
        integer = False


    header = None

    if filt == 'all':
        typeDict = vocabList 
        header = 'All words'
    elif integer:        
        for vocab in student_vocab:
            if student_vocab[vocab]['state'] == filt:
                typeDict[vocab] = vocabList[vocab]  
        header = 'All words categorized as ' + states[filt]      
    elif len(filt) == 3:        
        for vocab in vocabList:
            if search[filt] in vocabList[vocab]['tags']:
                typeDict[vocab] = vocabList[vocab]
        header = 'Words sorted by ' + search[filt]
    elif len(filt) == 1:
        for vocab in vocabList:
            if vocab[0] == filt:
                typeDict[vocab] = vocabList[vocab]
        header = 'Words sorted by "' + filt + '"'
    elif len(filt) == 2:                             
        for vocab in student_vocab:
            time_limit = {
                'ys' : [1, 'Updated since yesterday'],
                'wk' : [7, 'Updated in the last week'],
                'mn' : [30, 'Updated in the last month']
            }
            if student_vocab[vocab]['time'] > str(datetime.now() - timedelta(days=time_limit[filt][0])):
                typeDict[vocab] = vocabList[vocab]
        header=time_limit[filt][1] 

    
    return render_template('listVocab.html', title='Vocab', vocabList=typeDict, header=header, student_vocab=student_vocab)



@app.route('/update', methods=['POST', 'GET'])
@login_required 
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
       
    vocabList = loadMaster()

    randList = {}
    while len (randList) < count:
        random_vocab = random.choice(list(vocabList.keys()))
        if random_vocab in randList:
            pass
        else: 
            randList[random_vocab] = vocabList[random_vocab]
    
    
    
    return render_template('listRandom.html', title='Random', vocabList=vocabList, randList=randList)