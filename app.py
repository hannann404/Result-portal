from flask import Flask, render_template, request, flash, session, redirect, url_for
from dotenv import load_dotenv
import os
from hmac import compare_digest
from functools import wraps  # <-- 1. Needed for admin_required decorator
from werkzeug.utils import secure_filename
# from data import process_results

# --- STEP 1: SETUP APP ---
app = Flask(__name__)  # create your website
load_dotenv()  # load .env file

# secret key for session (login system needs this)
app.secret_key = os.getenv("SECRET_KEY")
password = os.getenv("PASSWORD")  # admin password from .env

# --- STEP 2: UPLOAD FOLDER CONFIG ---
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # create folder if not exists
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit

def allowed_file(filename):
    """Check if file is allowed (only csv)"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# --- STEP 3: SECURITY DECORATOR ---
# This is the guard that stops direct URL access
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # check if admin is logged in (session exists)
        if not session.get("is_admin"):
            flash("Please login first to access admin panel", "danger")
            return redirect(url_for('adminLogin'))  # send to login page
        return f(*args, **kwargs)
    return decorated_function

# --- STEP 4: PUBLIC ROUTE ---
@app.route('/', methods=['GET', 'POST'])  # home page /
def home():
    return render_template("portal.html")

# --- STEP 5: LOGIN ROUTE (PUBLIC) ---
@app.route('/login', methods=['GET', 'POST'])
def adminLogin():
    # if already logged in, go directly to admin panel
    if session.get("is_admin"):
        return redirect(url_for('adminDashboard'))
        
    if request.method == 'POST':    
       entered = request.form.get('password','')
       # secure compare to prevent timing attacks
       if compare_digest(entered, password):
           session["is_admin"] = True
           flash("Login successful!", "success")
           return redirect(url_for('adminDashboard'))  # use redirect, not render_template
       # error message 
       flash("Incorrect password", "danger")

    return render_template('adminLogin.html')

# --- STEP 6: PROTECTED ADMIN ROUTES ---
# These routes CANNOT be accessed by typing URL directly

@app.route('/admin')
@admin_required  # <-- protection added here
def adminDashboard():
    """Main admin panel page"""
    return render_template("admin.html")

@app.route("/admin/upload", methods=["GET", "POST"])
@admin_required  # <-- THIS STOPS ANYONE WITHOUT LOGIN
def adminUpload():
    """Upload CSV file - only for logged in admin"""
    if request.method == "POST":
        # check if file part exists
        if 'file' not in request.files:
            flash("No file selected", "danger")
            return redirect(request.url)
            
        file = request.files['file']
        
        # check if file is valid
        if file.filename == '':
            flash("No file selected", "danger")
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # secure the filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            
            # Optional: process your results file
            # process_results(filepath)
            
            flash(f"File {filename} uploaded successfully!", "success")
            return redirect(url_for('adminDashboard'))
        else:
            flash("Only CSV files allowed", "danger")
            
    return render_template("admin_upload.html")  # create this html file

# --- STEP 7: LOGOUT ROUTE ---
@app.route('/logout')
@admin_required
def logout():
    """Logout admin"""
    session.pop("is_admin", None)  # remove session
    flash("Logged out successfully", "info")
    return redirect(url_for('adminLogin'))

# --- STEP 8: RUN SERVER ---
if __name__ == '__main__':
    app.run(debug=True)  # start server