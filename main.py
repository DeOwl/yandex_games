from flask import Flask, request, render_template
from flask_ngrok import run_with_ngrok
from pickle import loads, dumps
import json
import os


app = Flask(__name__)
run_with_ngrok(app)

@app.route('/')
def main_page():
    return render_template("main_page.html")


if __name__ == '__main__':
    app.run()