from flask import Flask, render_template, request, Response
import time
import threading
from datetime import datetime
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwe123rqe123weqw31ewq'

socketio = SocketIO(app)
sending_to_socket = {}

cnt_short = cnt_long = old = 0

def incr():
    global cnt_long
    while True:
        time.sleep(1)
        cnt_long += 1

thread = threading.Thread(target=incr)
thread.start()

def answer(userMess):
    if "thời tiết" in userMess:
        return "Hôm nay thời tiết rất đẹp. Bạn nên ra ngoài dạo phố."
    elif "thứ mấy" in userMess:
        if datetime.today().weekday() == 6:
            return "Hôm nay là Chủ nhật"
        else:
            return "Hôm nay là thứ " + str(datetime.today().weekday()+2)
    elif "mấy giờ" in userMess:
        return "Bây giờ là " + datetime.today().strftime("%H:%M:%S")
    elif "ngày bao nhiêu" in userMess:
        return "Hôm nay là  " + datetime.today().strftime('%d-%m-%Y')
    else:
        return 'Xin lỗi. Tôi không có hiểu biết về vấn đề này.'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/short', methods = ['GET', 'POST'])
def short_handler():
    global cnt_short
    if request.method == 'GET':
        return render_template('short.html')
    elif request.method == 'POST':
        cnt_short += 1
        userMess=request.form.get('content')
        if userMess == None:
                return "Hãy hỏi tôi điều gì đó!!!"
        else:
            cnt_short = 0
            return answer(userMess)
    else:
        return Response('', status=405)

@app.route('/long', methods = ['GET', 'POST'])
def long_handler():
    global cnt_long
    global old
    if request.method == 'GET':
        return render_template('long.html')
    elif request.method == 'POST':
        userMess=request.form.get('content')
        if userMess == None:
            while cnt_long % 10 != 0 or old == cnt_long:
                pass
            old = cnt_long
            time.sleep(1)
            return "Hãy hỏi tôi điều gì đó"
        else:
            cnt_long = 1
            return answer(userMess)
    else:
        return Response('', status=405)

@app.route('/socket')
def socket_handler():
    return render_template('socket.html')

@socketio.on('connect')
def on_connect():
    sending_to_socket[request.sid] = True
    auto = threading.Thread(target=auto_chat, args=(request.sid,))
    auto.start()


@socketio.on('disconnect')
def on_disconnect():
    sending_to_socket[request.sid] = False

@socketio.on('message')
def on_message(data, methods = ['GET', 'POST']):
    ans = answer(data)
    socketio.send({'ans': ans}, to=request.sid)

def auto_chat(sid):
    global cnt_long
    while True:
        if cnt_long %5 == 0:
            socketio.send({'ans': "Hãy hỏi tôi bất kì điều gì!!"}, to=sid)
        else:
            pass
        time.sleep(1)
 
if __name__ == '__main__':
    socketio.run(app, debug=True)