from werkzeug.security import generate_password_hash, check_password_hash

users = {
    "petp-admin": generate_password_hash("petp-admin"),
    "petp": generate_password_hash("petp")
}

port = 5555
