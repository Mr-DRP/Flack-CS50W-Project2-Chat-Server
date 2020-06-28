import os
from datetime import datetime
from flask import Flask,render_template, request,session, redirect, url_for, jsonify, abort
from flask_socketio import SocketIO, emit
from flask_session import Session
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

chatroom = ['general']  # default room
usernames = []
messagedict = {'general': []}  # messages of each room

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['username']=='':
            return redirect(url_for('index'))
        session['username'] = request.form['username']
        session['channel'] = 'general'
        usernames.append(session['username'])
        #print(usernames)
        return redirect(url_for('index'))
    if "username" in session:
        if session['channel'] in chatroom:
            channelName = session['channel']
        else:
            channelName = 'general'
        return redirect(url_for('channel',channelName= channelName))
    return render_template('index.html', chatrooms = chatroom)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/channel/<channelName>', methods=['GET', 'POST'])
def channel(channelName):
    if "username" in session:
        if session['username'] not in usernames:
            usernames.append(session['username'])
    if channelName not in chatroom:
        abort(404)
    session['channel'] = channelName
    print(usernames)
    return render_template('index.html', chatrooms = chatroom, active = channelName)
    
@app.route('/listmessages', methods=['POST'])
def listmessages():
    return jsonify({"message":messagedict[session['channel']],"channel":session['channel']})
    

@socketio.on('sendMessage')
def message(data):
    message = data['message']
    time = datetime.now().strftime("%H:%M, %d %b")
    user = session.get("username")
    msg = dict(
        user = user, time= time, message = message
    )
    channel = session['channel']
    messagelist = messagedict[channel]
    if len(messagelist) == 100:
        del messagelist[0]
    messagelist.append(msg)
    #print(messagedict)
    emit('received message', {"message": message,"time": time, "user": user, "channel": session['channel']}, broadcast=True)

@socketio.on('createChannel')
def channelcreate(data):
    channel = data['name']
    if channel in chatroom:
        emit('error create',{"message":"Channel name already exists."})
    else:
        chatroom.append(channel)
        messagedict[channel] = []
        emit('channel create', {"channelname":channel}, broadcast=True)