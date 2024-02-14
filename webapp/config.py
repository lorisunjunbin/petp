from werkzeug.security import generate_password_hash, check_password_hash

port = 5555

shared_folder = "shared"

users = {
    "petp-admin": generate_password_hash("petp-admin"),
    "petp": generate_password_hash("petp")
}
