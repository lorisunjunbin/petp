import os
from flask import Flask, send_from_directory, render_template, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from config import users, port

app = Flask(__name__)
auth = HTTPBasicAuth()


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/')
@auth.login_required
def home():
    return render_template('index.html')


@app.route('/<path:path>')
@auth.login_required
def all_routes(path):
    return redirect('/')


if __name__ == "__main__":
    app.run(port=port)
