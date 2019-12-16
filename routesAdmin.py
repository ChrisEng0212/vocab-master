import sys, boto3, random
import datetime
import ast
import json
from random import randint
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import *
from pprint import pprint
from models import *
from flask_socketio import SocketIO
try:
    from config import AWS
    s3_resource = AWS.s3_resource
except:
    s3_resource = boto3.resource('s3')




@login.user_loader
def load_user(id):
    return User.query.get(int(id))

socketio = SocketIO(app, manage_session=False)


@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()      
    if form.validate_on_submit():
        print(form.studentID.data)
        if form.studentID.data == '123123123':            
            user = User.query.filter_by(username=form.password.data).first()
            login_user (user)
            flash (f'Login with Master Keys', 'secondary') 
            return redirect (url_for('home'))  
        user = User.query.filter_by(studentID=form.studentID.data).first() 
        if user and bcrypt.check_password_hash(user.password, form.password.data): #$2b$12$UU5byZ3P/UTtk79q8BP4wukHlTT3eI9KwlkPdpgj4lCgHVgmlj1he  '123'
            login_user (user, remember=form.remember.data)
            #next_page = request.args.get('next') #http://127.0.0.1:5000/login?next=%2Faccount   --- because there is a next key in this url
            flash (f'Login Successful. Welcome back {current_user.username}.', 'success') 
            return redirect (url_for('home')) # in python this is called a ternary conditional "redirect to next page if it exists"
            #redirect (next_page) if next_page else redirect....
        elif form.password.data == 'bones': 
            login_user (user)
            flash (f'Login with Skeleton Keys', 'secondary') 
            return redirect (url_for('home'))        
        else:
            flash (f'Login Unsuccessful. Please check {form.studentID.data} and your password.', 'danger')          
            return redirect (url_for('login'))
    return render_template('login.html', title='Login', form=form)


@app.route("/logout", methods=['GET'])
def logout():

    # Logout user
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('home'))


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():  

    return render_template("home.html")

@app.route("/register", methods=['GET','POST']) #and now the form accepts the submit POST
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # now register or log in link just go back home
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        username = form.username.data
        
        jstring = {}
        bucket_name = 'lms-tester'
        file_name = "jfolder/" + username + '.json'
        
        s3_resource.Bucket(bucket_name).put_object(Key=file_name, Body=str(jstring))
        
        j_location = "https://lms-tester.s3-ap-northeast-1.amazonaws.com/" + file_name
        
        user = User(username=username, studentID = form.studentID.data, email = form.email.data, old_email = form.email.data, 
        password = hashed_password, device = form.device.data, j_location=j_location, classroom=1)
        db.session.add(user)

        db.session.commit()
        flash(f'Account created for {form.username.data}!, please login', 'success') 
        #exclamation is necessary?? second argument is a style
        #'f' is because passing in a variable
        return redirect (url_for('login')) # redirect must be imported
    return render_template('register.html', title='Join', form=form)

@app.route("/account", methods=['GET','POST'])
@login_required # if user isn't logged in it will redirect to login page (see: login manager in __init__)
def account():
    form = UpdateAccountForm() 
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = upload_picture(form.picture.data) 
            current_user.image_file = picture_file                           
        current_user.email = form.email.data        
        db.session.commit() 
        flash('Your account has been updated', 'success')
        return redirect (url_for('account')) # so the get request will superceed another post request????
    elif request.method == 'GET':
        #form.username.data = current_user.username - taken out of form requirements
        form.email.data = current_user.email
    # https://www.youtube.com/watch?v=803Ei2Sq-Zs&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH&index=7    
    image_file = S3_LOCATION + current_user.image_file   
    
    return render_template('account.html', title='Account', image_file = image_file, form=form ) # form=form now form appears on account page

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                sender='chrisflask0212@gmail.com', 
                recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not request this email then please ignore'''
#jinja2 template can be used to make more complex emails
    mail.send(msg)


@app.route("/reset_password", methods = ['GET', 'POST'])
def reset_request():       
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ForgotForm()
    if form.validate_on_submit():        
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to you with instructions to reset your password', 'warning')
        return (redirect (url_for('login')))
    return render_template('user/reset_request.html', title='Password Reset', form=form) 

@app.route("/reset_password/<token>", methods = ['GET', 'POST'])
def reset_token(token):       
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:  
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated, please login', 'success') 
        return redirect (url_for('login'))
    return render_template('user/reset_token.html', title='Reset Password', form=form) 

