#-*-coding:utf-8-*-

from flask import Flask, render_template, redirect
from flask import request
from flask_bootstrap import Bootstrap
#from flask_sqlalchemy import SQLAlchemy
import pymysql.cursors
from flask_wtf import Form
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pagedown import PageDown
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired

import time

def create_app():
    app = Flask(__name__)
    return app

app = create_app()


bootstrap = Bootstrap(app)
pagedown = PageDown()
pagedown.init_app(app)
app.config.from_object('config')
#db = SQLAlchemy(app)
#import models

connect = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='root',
    db='bolg',
)


@app.route('/')
def hello_world():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>' % user_agent

@app.route('/page')
def addpage():
    form = PostForm(request.form)
    return render_template('page.html', form=form)

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello,%s!</h1>' % name

@app.route('/hello/<pageN>', methods=['GET', 'POST'])
def hello(pageN):
    #page = request.args.get('page', 1, type=int)
    if (getPostsRows()[0][0]) % 6 > 0:
        pageNum = (getPostsRows()[0][0])/6 + 1
    else:
        pageNum = (getPostsRows()[0][0])/6
    if int(pageN) > int(pageNum) or int(pageN) <= 0:
        pageN = 1
    posts = sreachall((int(pageN) * 6) - 1)
    titAll = sreachTit()

    listTit = []
    alllist = []
    # 0:ID , 1:time ,2:title 3:body ,4:author
    for post in posts:
        alllist.append({'author': {'name': post[4]}, 'body': post[3],\
                       'title': post[2], 'time': post[1].strftime("%a %b %d %Y")})

    for tit in titAll:
        listTit.append({'title': tit[0]})

    return render_template('index.html', posts=alllist, pageN=pageN,\
                           int=int, pageNum=pageNum, listTit=listTit)

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = PostForm()
    if form.validate_on_submit():
        createtime = '2017-7-5'
        body = form.body.data
        title = form.title.data

        number = insertPost(createtime, body, 'ht', title)

        if int(number) > 0:
            return redirect('/hello/1')
    else:
        return render_template('page.html', form=form)

@app.route('/post/<title>')
def readPost(title):

    post = sreachPost(title)
    postList = []
    postList.append({'title': post[0][2], 'body': post[0][3]})
    return render_template('post.html', post=postList)

@app.route('/bs')
def bs():
    return render_template('bs.html', name='ht')


def sreach():
    cursor = connect.cursor()
    str = '阿斯顿'
    #sql = "INSERT INTO users (username) VALUES ( '阿斯顿' )"
    #sql = "alter table users add COLUMN password varchar(64)"
    sql = "select * from users where id =3"
    cursor.execute(sql)
    #for row in cursor.fetchall():
    #   print(row)

    #connect.commit()
    #print('成功插入', cursor.rowcount, '条数据')
    return cursor.fetchall()

def sreachall(num):
    try:
        connect.open

        with connect.cursor() as cursor:
            sql = "SELECT * from posts order by ID DESC limit {}, 6  ".format(num)
            cursor.execute(sql)
            result = cursor.fetchall()
            connect.commit()
            return result

    finally:
        connect.commit()

def sreachPost(title):
    try:
        connect.open

        with connect.cursor() as cursor:
            sql = "SELECT * FROM posts WHERE title = '{}'".format(title)
            cursor.execute(sql)
            result = cursor.fetchall()
            connect.commit()
            return result
    finally:
        connect.commit()


def sreachTit():
    try:
        connect.open

        with connect.cursor() as cursor:
            sql = "SELECT title FROM posts  ORDER BY createtime DESC limit 10 "
            cursor.execute(sql)
            result = cursor.fetchall()
            connect.commit()
            return result
    finally:
        connect.commit()


def insertPost(time, post, author, title):
    try:
        connect.open
        with connect.cursor() as cursor:
            sql = "INSERT INTO posts (author,createtime,body,title) VALUES\
                  (\'{}\',\'{}\',\'{}\',\'{}\')".format(author, time, post, title)
            cursor.execute(sql)
            number = cursor.rowcount
            connect.commit()
            return number

    finally:
        connect.commit()

def getPostsRows():
    try:
        connect.open
        with connect.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM posts"
            cursor.execute(sql)
            number = cursor.fetchall()
            connect.commit()
            return number

    finally:
        connect.commit()

def setpass():
    password_hash = generate_password_hash('123123')

    cursor = connect.cursor()
    sql = "UPDATE users SET pwd = \'{}' WHERE id = 3 ".format(password_hash)
    cursor.execute(sql)
    print("!!!", cursor.rowcount)

def passw():
    for i in sreach():
        if check_password_hash(i[3], '123'):
            print('正确！！！')
        break

    print('错误！！！')


class PostForm(Form):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body')
    sumbit = SubmitField('submit')

if __name__ == '__main__':
    app.run()