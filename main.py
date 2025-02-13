from flask import Flask, render_template, request, redirect, flash, abort


app = Flask(__name__) 


@app.route("/")
def index():
    return render_template("home_page.html.jinja")