from flask import Flask, url_for, request, session, g, flash
from flask.templating import render_template
from werkzeug.utils import redirect
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
import nltk
nltk.download('popular')
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model
import json
import random
from flask import Flask, render_template, request
from contextlib import redirect_stdout
from io import StringIO
from pyngrok import ngrok
from datetime import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.static_folder = 'static'

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'crudapplication_db'):
        g.crudapplication_db.close()

def get_current_user():
    user = None
    if 'user' in session:
        user = session['user']
        db = get_database()
        user_cur = db.execute('select * from users where name = ?', [user])
        user = user_cur.fetchone()
    return user


@app.route('/')
def index():
    user = get_current_user()
    return render_template('home.html', user = user)

@app.route('/login', methods = ["POST", "GET"])
def login():
    user = get_current_user()
    error = None
    db = get_database()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user_cursor = db.execute('select * from users where name = ?', [name])
        user = user_cursor.fetchone()
        if user:
            if check_password_hash(user['password'], password):
                session['user'] = user['name']
                flash('logged in successfully')
                return redirect(url_for('dashboard'))
            else:
                error = "Username or Password did not match, Try again."
        else:
            error = 'Username or password did not match, Try again.'
    return render_template('login.html', loginerror = error, user = user)

@app.route('/register', methods=["POST", "GET"])
def register():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = get_current_user()
    db = get_database()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        dbuser_cur = db.execute('select * from users where name = ?', [name])
        existing_username = dbuser_cur.fetchone()
        if existing_username:
            return render_template('register.html', registererror = 'Username already taken , try different username.')
        db.execute('insert into users ( name, password) values (?, ?)',[name, hashed_password])
        db.commit()
        return redirect(url_for('index'))
    return render_template('register.html', user = user)

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    db = get_database()
    emp_cur = db.execute('select * from emp')
    allemp = emp_cur.fetchall()
    return render_template('dashboard.html', user = user, allemp = allemp)
import os

# Define the path for the upload folder
UPLOAD_FOLDER = os.path.join('static')

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set the upload folder in the app configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/addnewemployee', methods=["POST", "GET"])
def addnewemployee():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = get_current_user()

    if request.method == 'POST':
        # Proceed with saving employee details
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        salary = request.form['salary']
        Performance = request.form['Performance']
        skills = request.form['skills']
        total_project = request.form['total_project']
        suggestion = request.form['suggestion']
        job_role = request.form['job_role']
        academics = request.form['academics']
        # Check if an image was uploaded
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Save the uploaded image to the folder
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            else:
                # If no image is uploaded, set img_path to None
                img_path = None
        else:
            # If no image is uploaded, set img_path to None
            img_path = None

        db = get_database()
        db.execute('INSERT INTO emp (name, email, phone, address, salary, Performance, skills, total_project, suggestion, job_role, academics, img_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   [name, email, phone, address, salary, Performance, skills, total_project, suggestion, job_role, academics, img_path])
        db.commit()
        flash('employee added successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('addnewemployee.html', user=user)

@app.route('/singleemployee/<int:empid>')
def singleemployee(empid):
    user = get_current_user()
    db = get_database()
    emp_cur = db.execute('select * from emp where empid = ?', [empid])
    single_emp = emp_cur.fetchone()
    return render_template('singleemployee.html', user = user, single_emp = single_emp)

@app.route('/fetchone/<int:empid>')
def fetchone(empid):
    user = get_current_user()
    db = get_database()
    emp_cur = db.execute('select * from emp where empid = ?', [empid])
    single_emp = emp_cur.fetchone()
    return render_template('updateemployee.html', user = user, single_emp = single_emp)

@app.route('/deleteemp/<int:empid>', methods=["POST"])
def deleteemp(empid):
    if 'user' not in session:
        return redirect(url_for('login'))

    user = get_current_user()
    if request.method == 'POST':
        db = get_database()
        db.execute('DELETE FROM emp WHERE empid = ?', [empid])
        db.commit()
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', user=user)

@app.route('/updateemployee', methods=["POST", "GET"])
def updateemployee():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = get_current_user()
    if request.method == 'POST':
        empid = request.form['empid']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        salary = request.form['salary']
        Performance = request.form['Performance']
        skills = request.form['skills']
        total_project = request.form['total_project']
        job_role = request.form['job_role']
        suggestion = request.form['suggestion']
        academics = request.form['academics']
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing_image_path = request.form.get('existing_image_path', '')
        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Save the uploaded image to the folder
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
                img_path = os.path.join(image.filename)
            else:
                # If no new image is uploaded, use the existing image path
                img_path = request.form['existing_image_path']

        db = get_database()
        db.execute('UPDATE emp SET name = ?, email = ?, phone = ?, address = ?, salary = ?, Performance = ?, skills = ?, total_project = ?, job_role = ?, suggestion = ?, academics = ?, img_path = ?, last_updated = ? WHERE empid = ?', 
                   [name, email, phone, address, salary, Performance, skills, total_project, job_role, suggestion, academics, img_path, last_updated, empid])
        db.commit()
        flash('employee updated successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('updateemployee.html', user=user, existing_image_path=existing_image_path)


@app.route('/logout')
def logout():
    print("Logging out...")
    session.pop('user',None)
    print("User session cleared")
    flash('Logged Out Successfully')
    return redirect(url_for('index'))

lemmatizer = WordNetLemmatizer()
model = load_model('model.h5')

intents = json.loads(open('data.json').read())
words = pickle.load(open('texts.pkl', 'rb'))
classes = pickle.load(open('labels.pkl', 'rb'))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']

    for intent in list_of_intents:
        if intent['tag'] == tag:
            responses = intent['responses']

            if 'response_with_links' in intent:
                links_response = intent['response_with_links']
                result = random.choice(responses)
                link_texts = []
                for link in links_response:
                    link_texts.append(f"{link['message']}<a href='{link['link']}' target='blank'>{link['text']}</a><br><img width='200' height='150' alt='.' src='{link['link']}' </img>")
                return {"text": result + " ".join(link_texts), "link": True}
            else:
                result = random.choice(responses)
                return {"text": result, "link": False}

    return {"text": "I'm sorry, I don't understand that.", "link": False}

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)

    response_text = res["text"]
    response_link = res.get("link",'')
    link_text = res.get("link_text", "")

    if response_link:
        return f"{response_text}<br>"
    else:
        return response_text



@app.route("/cbot")
def cbot():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    responses = chatbot_response(userText)

    return json.dumps(responses)
if __name__ == '__main__':
    app.run(debug = True)