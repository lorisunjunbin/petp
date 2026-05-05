import os
import secrets
from pathlib import Path
from flask import Flask, send_from_directory, render_template, request, jsonify, abort, session, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from config import users, port, shared_folder
from translations import get_locale, make_translator
from utils import Utils

app = Flask(__name__)
app.secret_key = os.getenv("WEBAPP_SECRET_KEY", secrets.token_hex(32))
auth = HTTPBasicAuth()
WEBAPP_DIR = Path(__file__).resolve().parent
LOCAL_IMAGE_DIR = WEBAPP_DIR / 'static' / 'images'
PROJECT_IMAGE_DIR = (WEBAPP_DIR / '..' / 'image').resolve()
BUILD_ASSETS_DIR = WEBAPP_DIR / 'build_assets'


@app.context_processor
def inject_i18n():
    locale = get_locale()
    # Build lang-switch URLs that preserve the current path but swap ?lang=
    base = request.path
    return {
        "t": make_translator(locale),
        "locale": locale,
        "url_lang_en": f"{base}?lang=en",
        "url_lang_zh": f"{base}?lang=zh",
    }


# static folder for static files.
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


# PETP project image assets — self-contained for Docker.
@app.route('/petp-image/<path:path>')
def serve_petp_image(path):
    local_target = (LOCAL_IMAGE_DIR / path)
    if local_target.is_file():
        return send_from_directory(str(LOCAL_IMAGE_DIR), path)

    build_target = (BUILD_ASSETS_DIR / path)
    if build_target.is_file():
        return send_from_directory(str(BUILD_ASSETS_DIR), path)

    fallback_target = (PROJECT_IMAGE_DIR / path)
    if fallback_target.is_file():
        return send_from_directory(str(PROJECT_IMAGE_DIR), path)

    abort(404)


# Basic Auth for API routes (programmatic access).
@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


def _session_login_required(f):
    """Decorator: redirect to /login if the user has no active session."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# page - home
@app.route('/')
def home():
    return render_template('index.html')


# page - about PETP
@app.route('/about')
def about():
    return render_template('about.html')


# page - login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('file_viewer'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username in users and check_password_hash(users[username], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('file_viewer'))
        error = 'Invalid username or password.'
    return render_template('login.html', error=error)


# page - logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# page - file viewer (session-protected)
@app.route('/fileviewer')
@_session_login_required
def file_viewer():
    return render_template('fileviewer.html')


# shared folder for file download (session-protected).
@app.route('/' + shared_folder + '/<path:path>', methods=['POST'])
@_session_login_required
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
    app.run(host="0.0.0.0", port=port)
