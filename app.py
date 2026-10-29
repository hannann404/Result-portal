from flask import Flask , render_template

app = Flask(__name__)  # create your website

@app.route('/')  # when someone opens home page /
def home():
    return "Hello, Result System is running!"

app.run(debug=True)  # start server