from flask import Flask , render_template , request , flash , session
from dotenv import load_dotenv
import os
from hmac import compare_digest

app = Flask(__name__)  # create your website
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
password = os.getenv("PASSWORD")

# default route  
@app.route('/',methods=['GET','POST'])  # when someone opens home page /
def home():
    return render_template("portal.html")

# login route
@app.route('/login',methods=['GET','POST'])
def adminLogin():
    if request.method == 'POST':    
       entered = request.form.get('password','')
       # check entered password and original password
       if compare_digest(entered, password):
           session["is_admin"] = True
           # admin route
           return render_template("admin.html")
       # error message 
       flash("incorrect password")

    return render_template('adminLogin.html')



app.run(debug=True)  # start server