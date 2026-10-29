from flask import Flask , render_template

app = Flask(__name__)  # create your website

@app.route('/')  # when someone opens home page /
def home():
    return render_template("portal.html")

@app.route('/admin')
def admin_panel():
    return render_template("admin.html")

app.run(debug=True)  # start server