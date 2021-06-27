import sqlite3
from flask import Flask, render_template, url_for,request,redirect,make_response
from threading import Thread
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import hashlib
import json

app_root = os.path.dirname(os.path.abspath(__file__))
warning=''
nocontentwarning=''
app=Flask(__name__)
app.config['SECRET_KEY']="szykopyc"

def getDetailsRow(username):
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  cur.execute(f'''SELECT rowid,* FROM logindetails WHERE username='{username}';''')
  data=cur.fetchall()
  con.close()
  return data

def init():
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  cur.execute('''CREATE TABLE posts(date TEXT NOT NULL, username TEXT NOT NULL, displayName TEXT,post TEXT NOT NULL, imagePath TEXT);''')
  cur.execute('''CREATE TABLE logindetails(username TEXT, displayname TEXT, passwordHashed TEXT);''')
  con.commit()
  con.close()

def post(author,textToPost,displayName,imageURL=''):
  now = datetime.now()
  date = str(now.strftime("%d %B %Y"))
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  try:
    cur.execute(f'''INSERT INTO posts(date,username,displayName,post,imagePath) VALUES('{date}','{author}','{displayName}','{textToPost}','{imageURL}');''')
    cur.execute(f'''SELECT postsArray FROM userposts WHERE username='{author}';''')
    data=cur.fetchall()
    cur.execute(f'''SELECT MAX(rowid) from posts;''')
    data2=cur.fetchall()
    data2=data2[0][0]
    print(data2)
    data=data[0][0]
    print(data)
    if data!='[]':
      data=data[1:-1]
      data=data.split(',')
      data=list(data)
      print(data)
      print(data2)
      data.append(str(data2))
      print(data)
      data=list(map(int,data))
      data=str(data)
      print(data)
      cur.execute(f'''UPDATE userposts SET postsArray='{data}' WHERE username='{author}';''')
    else:
      cur.execute(f'''UPDATE userposts SET postsArray='[{data2}]' WHERE username='{author}';''')
    
    

  except Exception as e:
    print(e)
  con.commit()
  con.close()

def showPosts(searchParameter=None):
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  if searchParameter==None:
    cur.execute('''SELECT rowid,* FROM posts;''')
  
  elif searchParameter[0]=='@':
      cur.execute(f'''SELECT rowid,* FROM posts WHERE username='{searchParameter}';''')
  else:
    cur.execute(f'''SELECT rowid,* FROM posts WHERE displayName='{searchParameter}' OR post = '{searchParameter}'; ''')
  data=cur.fetchall()
  con.close()
  return data

def deletePosts(arrayIDs):
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  cur.execute(f'''DELETE FROM posts WHERE 1=1;''')
  con.commit()
  con.close()

def getMaxID():
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  cur.execute('''SELECT MAX(rowid) FROM posts;''')
  max=cur.fetchall()
  con.close()
  return max

def userPosts(username):
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  cur.execute(f'''SELECT * FROM userposts WHERE username='{username}';''')
  data=cur.fetchall()
  con.commit()
  con.close()
  return data

@app.route('/createpost',methods=['POST'])
def createPost():
  global warning
  global nocontentwarning
  if request.method=='POST':
    authorName = request.cookies.get('userName')
    displayName=request.cookies.get('displayName')
    postContent = request.form['postContent']
    try:
      file= request.files['file']
    except Exception as e:
      print(e)
    if postContent!='' or file and file.filename.endswith(('.jpeg','.jpg','.png','.gif','.jfif','.mp4','.mov','.webm','.ogg','.mpeg','.m4p')):
      try:
        file_name = file.filename
      except:
        file_name=''

      if file_name!='' and file_name.endswith(('.jpeg','.jpg','.png','.gif','.jfif','.mp4','.mov','.webm','.ogg','.mpeg','.m4p','.PNG')):
          destination = 'static/files/'+file_name
      try:
        file.save(destination)
      except:
        pass
      resp = make_response(redirect('/'))
      resp.set_cookie('nocontentwarning', '',expires=0)   
      try:
        post(authorName,postContent,displayName,destination)
      except:
        post(authorName,postContent,displayName) 
      return resp

    else:
        resp = make_response(redirect('/'))
        resp.set_cookie('nocontentwarning', "You haven't entered anything to post, please enter some text or upload a file")      
        return resp

@app.route('/login',methods=['POST', 'GET'])
def login():
  if request.method == 'POST':
      user = request.form['uname']
      if user[0]!='@':
        user='@'+user 
      passw = request.form['pword']
      passw=passw.encode()
      resp = make_response(redirect('/'))
      newp = hashlib.sha256(passw)
      newp=newp.hexdigest()
      login_details=getDetailsRow(user)
      try:
        if login_details[0][1]==user and login_details[0][3]==newp:
          resp.set_cookie('userName', user)
          resp.set_cookie('userPassword', newp)
          resp.set_cookie('displayName', login_details[0][2])
          return resp
        else:
          return 'incorrect details'
      except:
        return 'incorrect details'


@app.route('/logout',methods=['POST', 'GET'])
def logout():
  if request.method == 'POST':
      resp = make_response(redirect('/'))
      resp.set_cookie('userName','',expires=0)
      resp.set_cookie('userPassword','',expires=0)
      resp.set_cookie('displayName','',expires=0)
  return resp

@app.route('/register',methods=['POST','GET'])
def register():
  if request.method=="POST":
    username = request.form['username']
    username='@'+username
    display = request.form['displayname']
    password=request.form['password']
    confirm=request.form['confirm']
    if password != confirm:
      return 'Passwords dont match'
    elif len(getDetailsRow(username))>0:
      return 'Username already taken'
    else:
      password=hashlib.sha256(password.encode()).hexdigest()
      con = sqlite3.connect("PostPosts.db")
      cur = con.cursor()
      cur.execute(f'''INSERT INTO logindetails(username,displayname,passwordHashed) VALUES ('{username}','{display}','{password}');''')
      cur.execute(f'''INSERT INTO userposts(username,postsArray) VALUES('{username}','[]');''')
      con.commit()
      con.close()
      return redirect('/')
  return render_template('register.html')

@app.route('/search', methods=['POST','GET'])
def searchPost():
  if request.method=="POST":
    searchQuery=request.form['searchQuery']
    if searchQuery[0]=='@':
      return redirect(f'/profiles/{searchQuery[1:]}')
    else:
      return redirect(f'/profiles/{searchQuery}')

@app.route("/profiles/<username>")
def profiles(username):
  con=sqlite3.connect('PostPosts.db')
  cur=con.cursor()
  cur.execute(f'''SELECT * FROM userposts WHERE username='@'||'{username}';''')
  data=cur.fetchall()
  con.close()
  if data!=[]:
    posts=showPosts('@'+username)
    print(posts)
    try:
      return render_template('profile.html',username=username,posts=reversed(posts))
    except:
      return 'lmao'
  else:
    return 'USER DOESNT EXIST'

@app.route('/')
def home():
  posts=showPosts()
  userName = request.cookies.get('userName')
  userPassword=request.cookies.get('userPassword')
  noContentCookie=request.cookies.get('nocontentwarning')
  try:
    return render_template('index.html',posts=posts.reverse(),noContentCookie=noContentCookie,cookie=userName,passCookie=userPassword)
  except:
    return render_template('index.html',posts=posts, noContentCookie=noContentCookie,cookie=userName,passCookie=userPassword)



if __name__ ==  '__main__':
    app.run(host='0.0.0.0',debug=True)
