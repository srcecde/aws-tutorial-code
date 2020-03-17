from flask import Flask, render_template, url_for, redirect
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/home")
def home():
    return redirect(url_for('login'))

@app.route("/login")
def login():
    return render_template("login.html")
