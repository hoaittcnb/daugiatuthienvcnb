import time
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session,current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc,func
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, logout_user, login_required, current_user,UserMixin
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import schedule
import pandas as pd
import random
import pymsgbox
import time as ti
from flask_socketio import SocketIO, emit
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key')  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_SQLITE_USES_NAMED_TABLES'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)


socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# In-memory user and session store (replace with DB later)
# users_db = {}  # {username: password}
online_users = set()




app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'cnbactivities@gmail.com'  # Use your actual Gmail address
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')     # Use your generated App Password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    hopthu = db.Column(db.String(100), nullable=False)
    is_online = db.Column(db.Boolean, default=False)

    def __init__(self, username, fullname, hopthu, password):
        self.username = username
        self.fullname = fullname
        self.hopthu = hopthu
        self.password = password
class product(db.Model):
    idp = db.Column(db.Integer, primary_key=True,nullable=False,autoincrement=True)
    namep = db.Column(db.String(500), nullable=False)
    price_first=db.Column(db.Integer, nullable=False)
    qgrate=db.Column(db.Integer, nullable=False)
    datefdg = db.Column(db.Date, nullable=False)
    datetdg = db.Column(db.Date, nullable=False)
    sotien = db.Column(db.Integer, nullable=False)
    nguoidaugia = db.Column(db.String(500), nullable=False)
    iddg = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Show {self.title}>'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        fullname=request.form['fullname']
        hopthu=request.form['hopthu']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            new_user = User(username=username, password=hashed_password,hopthu=hopthu,fullname=fullname)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # login_user(user)
            session['user_id'] = user.id
            user.is_online = True
            db.session.commit()
            # flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/profile',methods=['GET', 'POST'])


def profile():

    if 'user_id' in session:
        user_id = session['user_id']
        user = db.session.get(User, user_id)

        # user = User.query.get(user_id)

        if request.method == 'POST':
            iddg = request.form['iddg']
            sotien = int(request.form['sotien'])
            nguoidaugia = user.username
            min_number = db.session.query(func.min(product.sotien)).filter_by(iddg=iddg).scalar()
            if min_number<100000:
                sotienthem=10000
            elif min_number<1000000:
                sotienthem=30000
            else:
                sotienthem=100000

            max_number1 = db.session.query(func.max(product.sotien)).filter_by(iddg= iddg ).scalar()
            max_number=max_number1+sotienthem
            if max_number is None or sotien >= max_number:
                new_product = product(namep='', price_first=0, qgrate=0, datefdg=datetime(2024, 7, 31, 10, 10, 10),
                                      datetdg=datetime(2024, 7, 31, 10, 10, 10), sotien=sotien, nguoidaugia=nguoidaugia,
                                      iddg=iddg)
                db.session.add(new_product)
                db.session.commit()
                # flash(f'Success! {sotien} is the largest number and has been added to the database.')
            else:
                flash(f'Vui lòng nhập giá đấu tối thiểu {format(max_number,",d")} cho vật phẩm này.')


        showr = product.query.filter_by(sotien= 0).order_by(product.idp).all()
        # shows = product.query.filter_by(namep = '' ).filter_by(iddg= 1 ).order_by(product.iddg,desc(product.sotien)).all()
        show1=product.query.filter_by(iddg= 1 ).order_by(product.iddg,desc(product.sotien)).all()
        show2=product.query.filter_by(iddg= 2 ).order_by(product.iddg,desc(product.sotien)).all()
        show3=product.query.filter_by(iddg= 3 ).order_by(product.iddg,desc(product.sotien)).all()
        show4 = product.query.filter_by(iddg= 4 ).order_by(product.iddg,desc(product.sotien)).all()
        show5 = product.query.filter_by(iddg= 5 ).order_by(product.iddg,desc(product.sotien)).all()
        show6 = product.query.filter_by(iddg= 6 ).order_by(product.iddg,desc(product.sotien)).all()
        show7= product.query.filter_by(iddg= 7 ).order_by(product.iddg,desc(product.sotien)).all()
        show8 = product.query.filter_by(iddg=8).order_by(product.iddg, desc(product.sotien)).all()
        show9 = product.query.filter_by(iddg=9).order_by(product.iddg, desc(product.sotien)).all()
        show10 = product.query.filter_by(iddg=10).order_by(product.iddg, desc(product.sotien)).all()
        show11 = product.query.filter_by(iddg=11).order_by(product.iddg, desc(product.sotien)).all()
        show12 = product.query.filter_by(iddg=12).order_by(product.iddg, desc(product.sotien)).all()
        show13 = product.query.filter_by(iddg=13).order_by(product.iddg, desc(product.sotien)).all()
        show14 = product.query.filter_by(iddg=14).order_by(product.iddg, desc(product.sotien)).all()
        show15 = product.query.filter_by(iddg=15).order_by(product.iddg, desc(product.sotien)).all()
        show16 = product.query.filter_by(iddg=16).order_by(product.iddg, desc(product.sotien)).all()
        show17 = product.query.filter_by(iddg=17).order_by(product.iddg, desc(product.sotien)).all()
        show18 = product.query.filter_by(iddg=18).order_by(product.iddg, desc(product.sotien)).all()
        show19 = product.query.filter_by(iddg=19).order_by(product.iddg, desc(product.sotien)).all()
        show20 = product.query.filter_by(iddg=20).order_by(product.iddg, desc(product.sotien)).all()
        show21 = product.query.filter_by(iddg=21).order_by(product.iddg, desc(product.sotien)).all()
        show22 = product.query.filter_by(iddg=22).order_by(product.iddg, desc(product.sotien)).all()
        show23 = product.query.filter_by(iddg=23).order_by(product.iddg, desc(product.sotien)).all()

        users = User.query.filter_by(is_online=True).all()

        return render_template('profile.html', users=users,user=user,showr=showr,show1=show1,show2=show2,show3=show3,show4=show4,show5=show5,show6=show6,show7=show7,show8=show8,show9=show9,show10=show10,show11=show11,show12=show12,show13=show13,show14=show14,show15=show15,show16=show16,show17=show17,show18=show18,show19=show19,show20=show20,show21=show21,show22=show22,show23=show23)
    else:
        flash('You need to log in first.', 'info')
        return redirect(url_for('login'))


@app.route('/account', methods=['GET', 'POST'])
def account():
    # user = current_user
    user_id = session['user_id']
    user = User.query.get(user_id)

    if request.method == 'POST':
        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        if check_password_hash(user.password, oldpassword):
            if newpassword==password:
                user.password = hashed_password
                db.session.commit()
                flash('Mật khẩu mới được cập nhật thành công', 'success')
            else:
               flash('Hai mật khẩu mới không giống nhau. vui lòng nhập lại', 'error')

        else:
            flash('Mật khẩu cũ không đúng. vui lòng nhập lại', 'error')


    return render_template('account.html',user=user)

@app.route('/gameluckydraw', methods=['GET', 'POST'])

def gameluckydraw():
    user_id = session['user_id']
    user = User.query.get(user_id)
    users = User.query.filter_by(is_online=True).all()
    listname=[]
    listname1=""
    listname2=''
    listloai1=""
    for user in users:
        listname.append(user.username)
        listname1=listname1+","+str(user.username)
    if request.method == 'POST':
        t = 1
        listloai=[]
        while (t == 1):
            a = random.choice(listname)
            ti.sleep(5)
            m = "xin chia buon cung {0}".format(a)
            flash('xin chia tay {0}'.format(m), 'success')
            pymsgbox.alert(m, 'thông báo')
            t = int(pymsgbox.prompt('Bạn có muốn loại tiếp không?'))
            listname.remove(a)
            listloai.append(a)
            for j in listname:
                listname2=listname2+j
            for i in listloai:
                listloai1=listloai1+","+i

            return render_template('gameluckydraw.html',user=user,users=users,listname1=listname1,listloai1=listloai1,listname2=listname2)
    return render_template('gameluckydraw.html', user=user, users=users, listname1=listname1, listloai1=listloai1,listname2=listname2)

@app.route('/gamemayman')

def gamemayman():
    # run_time = datetime.strptime('11:00:00', '%H:%M:%S').time()
    # now = datetime.now()
    # delay = ((datetime.combine(now, run_time) - now).total_seconds()) if ((datetime.combine(now, run_time) - now).total_seconds()) >0 else 0
    users = User.query.filter_by(is_online=True).all()
    listname = []
    listname1 = ""
    # listname2 = ''
    # listloai1 = ""
    useronline=0
    for user in users:
        listname.append(user.username)
        if useronline==0 :listname1 =str(user.username)
        else: listname1 = listname1 + ", " + str(user.username)
        useronline=useronline+1
    # listloai = []
    #
    # time.sleep(delay)
    # for i in range(0,5):
    #     a = random.choice(listname)
    #     ti.sleep(5)
    #     m = "xin chia buon cung {0}".format(a)
    #     flash('xin chia tay {0}'.format(m), 'success')
    #     listname.remove(a)
    #     listloai.append(a)
    # for j in listname:
    #     listname2 = listname2 + j
    # for i in listloai:
    #     listloai1 = listloai1 + "," + i

    # return render_template('gamemayman.html', users=users, listname1=listname1,listloai1=listloai1, listname2=listname2)
    return render_template('gamemayman.html', users=users, listname1=listname1,useronline=useronline)



def job():
    flash("Program is running at the scheduled time")

@app.route('/logout')
def logout():
    user = User.query.get(session['user_id'])
    user.is_online = False
    db.session.commit()
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/forget_pass', methods=['GET', 'POST'])
def forget_pass():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            dayso=random.randint(1,600000)
            newpass=username+str(dayso)
            hashed_password = generate_password_hash(newpass)
            user.password = hashed_password
            send_reset_email(user,newpass)
            db.session.commit()
            flash('Mật khẩu được gửi đến email của bạn. vui lòng check mail', 'success')
        else:
            flash('Người dùng không tồn tại. vui lòng nhập lại.', 'error')
    return render_template('forgetpass.html')

@app.route('/chatbox', methods=['GET', 'POST'])
def chatbox():
    user_id = session['user_id']
    user = User.query.get(user_id)
    return render_template('chatbox.html',user=user)

@app.route('/general', methods=['GET', 'POST'])
def general():
    user_id = session['user_id']
    user = User.query.get(user_id)
    return render_template('general.html',user=user)

def send_reset_email(user,newpassword):
    msg = Message('New Password',sender='cnbactivities@gmail.com',recipients=[user.hopthu])
    msg.body = f'''Mật mã mới của bạn là:{newpassword}'''
    mail.send(msg)





@login_manager.user_loader
def load_user(user_id):
    # return User.query.get(int(user_id))
    return db.session.get(User, int(user_id))

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            online_users.add(user.username)
            emit('user_list', list(online_users), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            online_users.discard(user.username)
            emit('user_list', list(online_users), broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            emit('receive_message', {'user': user.username, 'message': data['message']}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run(debug=True)
    socketio.run(app, debug=True, port=8051, allow_unsafe_werkzeug=True)

web_dau_gia/app.py
