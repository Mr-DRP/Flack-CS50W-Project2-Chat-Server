import os
from datetime import datetime
from flask import Flask,render_template, request,session, redirect, url_for
from flask_socketio import SocketIO, emit


app = Flask(__name__)
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
        usernames.append(session['username'])
        print(usernames)
        return redirect(url_for('index'))
    return render_template('index.html', chatrooms = chatroom, active = 'general')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/channel/<channelName>')
def channel(channelName):
    print(messagedict)
    session['channel'] = channelName
    return render_template('index.html', chatrooms = chatroom, active = channelName)
    
@socketio.on('sendMessage')
def message(data):
    message = data['message']
    time = datetime.now().strftime("%H:%M, %d %b")
    user = session.get("username")
    msg = dict(
        user = user, time= time, message = message
    )
    channel = session['channel']
    messagedict[channel].append(msg)
    print(messagedict)
    emit('received message', {"message": message,"time": time, "user": user}, broadcast=True)

@socketio.on('createChannel')
def channelcreate(data):
    channel = data['name']
    chatroom.append(channel)
    messagedict[channel] = []
    emit('channel create', {"channelname":channel})