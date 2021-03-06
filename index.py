# -*-coding:utf-8-*-

from flask import Flask, render_template, redirect, session, url_for, escape, request
from flask_bootstrap import Bootstrap
# from flask_sqlalchemy import SQLAlchemy
import pymysql.cursors
from flask_wtf import FlaskForm as From
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pagedown import PageDown
from wtforms import TextAreaField, SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired
import markdown
import datetime
from datetime import timedelta


def create_app():
    app = Flask(__name__)
    return app


app = create_app()

bootstrap = Bootstrap(app)
pagedown = PageDown()
pagedown.init_app(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
# import models

import contextlib

@contextlib.contextmanager
def mysql(host='localhost', port=3306, user='root', passwd='09apple', db='blog', charset='utf8'):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        yield cursor
    finally:
        conn.commit()
        cursor.close()
        conn.close()


@app.route('/')
def hello_world():
    user_agent = request.headers.get('User-Agent')
    return redirect('/hello/1')


@app.route('/page2')
def addpage():

    print(markdown.markdown('as', ['codehilite']))
    return render_template('demo.html')


@app.route('/user/<name>')
def user(name):
    return '<h1>Hello,%s!</h1>' % name


@app.route('/hello/<pageN>', methods=['GET', 'POST'])
def hello(pageN):
    # page = request.args.get('page', 1, type=int)
    pageNumall = getPostsRows()[0]['number']
    if pageNumall % 6 > 0:
        pageNum = pageNumall / 6 + 1
    else:
        pageNum = pageNumall / 6
    if int(pageN) > int(pageNum) or int(pageN) <= 0:
        pageN = 1
    posts = sreachall(((int(pageN) - 1) * 6))
    titAll = sreachTit()

    listTit = []
    alllist = []
    # 0:ID , 1:time ,2:title 3:body ,4:author
    for post in posts:
        alllist.append({'author': {'name': post['author']}, 'body': post['body'], \
                        'title': post['title'], 'time': post['createtime'].strftime("%Y-%m-%d")})
    for tit in titAll:
        listTit.append({'title': tit['title']})

    return render_template('index.html', posts=alllist, pageN=pageN, \
                           int=int, pageNum=pageNum, listTit=listTit)


@app.route('/add', methods=['GET', 'POST'])
def add():

    form = PostForm()
    if form.validate_on_submit():
        createtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

        body = form.body.data
        title = form.title.data

        number = insertPost(createtime, body, 'ht', title)

        if int(number) > 0:
            return redirect('/hello/1')
    else:
        if 'pwd' in session:
            return render_template('page.html', form=form)
        else:
            return render_template('bs.html', form=form)




@app.route('/getpwd', methods=['GET', 'POST'])
def addForPwd():
    form = PostFormPwd()
    if form.validate_on_submit():

        pwd = form.pwd.data
        # setpass()
        if passw(pwd) == 1:
            if request.method == 'POST':
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=30)
                session['pwd'] = request.form['pwd']
            form1 = PostForm()
            return render_template('page.html', form=form1)
        else:
            return render_template('bs.html', form=form)
    else:
        return render_template('bs.html', form=form)


@app.route('/post/<title>')
def readPost(title):
    post = sreachPost(title)
    postList = []
    postList.append({'title': post[0]['title'], 'body': markdown.markdown(post[0]['body'], extensions=['codehilite'])})
    return render_template('post.html', post=postList)


@app.route('/bs')
def bs():
    return render_template('bs.html', name='ht')


@app.route('/about')
def about():
    return render_template('about.html')


def sreachall(num):



        with mysql() as cursor:
            sql = "SELECT * from posts order by ID DESC limit {}, 6  ".format(num)
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result




def sreachPost(title):

        with mysql() as cursor:
            sql = "SELECT * FROM posts WHERE title = '{}'".format(title)
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result


def sreachTit():

        with mysql() as cursor:
            sql = "SELECT title FROM posts  ORDER BY createtime DESC limit 10 "
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result


def insertPost(time, post, author, title):

        with mysql() as cursor:
            args = (author, time, post, title)
            sql = "INSERT INTO posts (author,createtime,body,title) VALUES\
                  (%s, %s, %s, %s)"
            cursor.execute(sql, args)
            number = cursor.rowcount
            cursor.close()

            return number


def getPostsRows():

        with mysql() as cursor:
            sql = "SELECT COUNT(*) as number FROM posts"
            cursor.execute(sql)
            number = cursor.fetchall()
            cursor.close()
            return number




def setpass():
    password_hash = generate_password_hash('111')

    with mysql() as cursor:
        sql = "insert into user (id,username,password) VALUES (20,'ht','{}')".format(password_hash)
        cursor.execute(sql)
        cursor.close()
        return 1


        # cursor = connect.cursor()
        # sql = "UPDATE users SET pwd = \'{}' WHERE id = 3 ".format(password_hash)
        # cursor.execute(sql)
        # print("!!!", cursor.rowcount)


def sreach():
    with mysql() as cursor:

        sql = "select password from user where id =20 AND username = 'ht'"
        cursor.execute(sql)

        # for row in cursor.fetchall():
        #   print(row)
        # connect.commit()
        pwas = cursor.fetchall()
        cursor.close()
        return pwas


def passw(pwd):
    pwdL = sreach()
    pwd_byte = generate_password_hash(pwdL[0]['password'])

    if check_password_hash(pwdL[0]['password'], pwd):
        return 1



class PostForm(From):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body')
    sumbit = SubmitField('submit')
    pwd = PasswordField('pwd')


class PostFormPwd(From):
    sumbit = SubmitField('submit')
    pwd = PasswordField('pwd')


if __name__ == '__main__':
    app.run()
