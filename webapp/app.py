import os
from flask import Flask, send_from_directory, render_template, redirect, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from config import users, port, shared_folder
from utils import Utils

app = Flask(__name__)
auth = HTTPBasicAuth()


# static folder for static files.
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


# Basic Auth for the app login.
@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


# page - home
@app.route('/')
def home():
    return render_template('index.html')


# page - file viewer
@app.route('/fileviewer')
@auth.login_required
def file_viewer():
    return render_template('fileviewer.html')


# @app.route('/<path:path>')
# @auth.login_required
# def all_routes(path):
#     return redirect('/')

# shared folder for file download.
@app.route('/' + shared_folder + '/<path:path>', methods=['POST'])
@auth.login_required
def serve_shared(path):
    return send_from_directory(shared_folder, path)


@app.route('/api/v1/search/files/', methods=['GET'])
@auth.login_required
def search_files():
    query = request.args.get("q")
    files = Utils.collect_files(os.path.realpath(shared_folder),
                                file_name_lambda=lambda file_name: query in file_name if query is not None else True)
    return jsonify(files)


if __name__ == "__main__":
    app.run(port=port)
