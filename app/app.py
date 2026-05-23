import os, sqlite3
from functools import wraps
from flask import Flask, redirect, request, session, url_for, render_template, g
from authlib.integrations.requests_client import OAuth2Session
import requests as req

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

KC_URL     = os.environ["KEYCLOAK_URL"]
REALM      = os.environ["KEYCLOAK_REALM"]
CLIENT_ID  = os.environ["KEYCLOAK_CLIENT_ID"]
CLIENT_SEC = os.environ["KEYCLOAK_CLIENT_SECRET"]
REDIRECT   = os.environ["KEYCLOAK_REDIRECT_URI"]
DB_PATH    = os.environ.get("DATABASE", "/opt/intranet/app/intranet.db")

AUTH_URL   = f"{KC_URL}/realms/{REALM}/protocol/openid-connect/auth"
TOKEN_URL  = f"{KC_URL}/realms/{REALM}/protocol/openid-connect/token"
USERINFO   = f"{KC_URL}/realms/{REALM}/protocol/openid-connect/userinfo"
LOGOUT_URL = f"{KC_URL}/realms/{REALM}/protocol/openid-connect/logout"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            title   TEXT NOT NULL,
            content TEXT NOT NULL,
            author  TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/auth/login")
def login():
    oauth = OAuth2Session(CLIENT_ID, CLIENT_SEC, redirect_uri=REDIRECT,
                          scope=["openid", "profile", "email"])
    uri, state = oauth.create_authorization_url(AUTH_URL)
    session["oauth_state"] = state
    return redirect(uri)

@app.route("/auth/callback")
def callback():
    oauth = OAuth2Session(CLIENT_ID, CLIENT_SEC,
                          redirect_uri=REDIRECT,
                          state=session.get("oauth_state"))
    token = oauth.fetch_token(TOKEN_URL, authorization_response=request.url)
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    resp = req.get(USERINFO, headers=headers)
    userinfo = resp.json()
    session["user"] = {
        "username": userinfo.get("preferred_username"),
        "email":    userinfo.get("email"),
        "name":     userinfo.get("name", userinfo.get("preferred_username")),
    }
    return redirect(url_for("index"))

@app.route("/auth/logout")
def logout():
    session.clear()
    return redirect(LOGOUT_URL + "?redirect_uri=http://intranet.itway.local/")

@app.route("/")
@login_required
def index():
    db = get_db()
    news = db.execute("SELECT * FROM news ORDER BY created DESC").fetchall()
    return render_template("index.html", user=session["user"], news=news)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

with app.app_context():
    init_db()
