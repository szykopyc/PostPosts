import sqlite3
from flask import Flask, render_template, url_for,request,redirect
from threading import Thread
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app_root = os.path.dirname(os.path.abspath(__file__))
warning=''
nocontentwarning=''
app=Flask(__name__)
app.config['SECRET_KEY']="szykopyc"

def init():
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  cur.execute('''CREATE TABLE posts(id INT PRIMARY KEY,date TEXT NOT NULL, author TEXT NOT NULL, post TEXT NOT NULL, imagePath TEXT);''')
  con.commit()
  con.close()

def post(author,textToPost,imageURL=''):
  now = datetime.now()
  date = str(now.strftime("%d %B %Y"))
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  try:
    cur.execute(f'''INSERT INTO posts(date,author,post,imagePath) VALUES('{date}','{author}','{textToPost}','{imageURL}');''')
  except Exception as e:
    print(e)
  con.commit()
  con.close()

def showPosts():
  con = sqlite3.connect("PostPosts.db")
  cur = con.cursor()
  cur.execute('''SELECT rowid,date,author,post,imagePath FROM posts;''')
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
  global warning
  global nocontentwarning
  if request.method=='POST':
    authorName = request.form['authorName']
    if authorName !='':
      warning=''
      postContent = request.form['postContent']
      try:
        file= request.files['file']
      except Exception as e:
        print(e)
      if postContent!='' or file and file.filename.endswith(('.jpeg','.jpg','.png','.gif','.jfif','.mp4','.mov','.webm','.ogg','.mpeg','.m4p')):
        nocontentwarning=''
        try:
          file_name = file.filename
        except:
          file_name=''

        if file_name!='' and file_name.endswith(('.jpeg','.jpg','.png','.gif','.jfif','.mp4','.mov','.webm','.ogg','.mpeg','.m4p')):
          destination = 'static/files/'+file_name
        try:
          file.save(destination)
        except:
          pass

        try:
          post(authorName,postContent,destination)
        except:
          post(authorName,postContent)
        return redirect('/')

      elif file.filename.endswith(('.jpeg','.jpg','.png','.gif','.jfif','.mp4','.mov','.webm','.ogg','.mpeg','.m4p'))!=True:
        nocontentwarning="You have given an unsupported file type!"
        return redirect('/')


      else:
        nocontentwarning="You haven't given anything to post, please enter some content!"
        return redirect('/')
    else:
      warning="No display name entered, please enter one!"
      return redirect('/')
    

@app.route('/')
def home():
  posts=showPosts()
  try:
    return render_template('index.html',posts=posts.reverse())
  except:
    return render_template('index.html',posts=posts, noNameWarning=warning, noContent=nocontentwarning)

if __name__ ==  '__main__':
    app.run(host='0.0.0.0',debug=True)
