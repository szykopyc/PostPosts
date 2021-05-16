import sqlite3
from flask import Flask, render_template, url_for,request,redirect
from threading import Thread
from datetime import datetime

app=Flask(__name__)
app.config['SECRET_KEY']="szykopyc"

def init():
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  cur.execute('''CREATE TABLE posts(id INT PRIMARY KEY,date TEXT NOT NULL, author TEXT NOT NULL, post TEXT NOT NULL);''')
  con.commit()
  con.close()

def post(author,textToPost):
  now = datetime.now()
  date = str(now.strftime("%d %B %Y"))
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  try:
    cur.execute(f'''INSERT INTO posts(date,author,post) VALUES('{date}','{author}','{textToPost}');''')
  except Exception as e:
    print(e)
  con.commit()
  con.close()

def showPosts():
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  cur.execute('''SELECT rowid,date,author,post FROM posts;''')
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

@app.route('/createpost',methods=['POST'])
def createPost():
  authorName = request.form['authorName']
  postContent = request.form['postContent']
  post(authorName,postContent)
  return redirect('/')

@app.route('/deleteall',methods=['POST'])
def deleteAll():
  try:
    max=getMaxID()
    arrayOfIDs=[]
    for i in range(max[0][0]):
      arrayOfIDs.append(i)
    arrayOfIDs.append(len(arrayOfIDs))
    deletePosts(arrayOfIDs)
    arrayOfIDs=[]
    return redirect('/')
  except:
    return redirect('/')

@app.route('/')
def home():
  posts=showPosts()
  try:
    return render_template('index.html',posts=posts.reverse())
  except:
    return render_template('index.html',posts=posts)

if __name__ ==  '__main__':
    app.run(host='0.0.0.0')
