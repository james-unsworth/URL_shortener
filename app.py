from flask import Flask, request, redirect, render_template, jsonify
from urllib.parse import urlparse
import secrets
import sqlite3
from pathlib import Path
app = Flask(__name__)

MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = ["http", "https"]
DB_PATH = Path(__file__).resolve().parent / "url_map.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS url_map (shortened TEXT PRIMARY KEY, url TEXT)")

def error(msg: str, err_code: int):
    return jsonify({ "err_msg": msg}), err_code

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/shorten", methods=["POST"])
def shorten():

    def insert_entry( url: str):
        fail_count = 0
        while fail_count < 50:
            try:
                code = secrets.token_urlsafe(5)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO url_map VALUES (?, ?)", (code, url))
                return code
            except sqlite3.IntegrityError:
                fail_count += 1
        return None

    if not isinstance(request.get_json(silent=True), dict): return error("Request body must be a JSON object, for example {\"url\": \"example.com\"}.", 400)

    url = request.json.get("url")
    if not isinstance(url, str): return error("Please enter a valid URL.", 400)
    url = url.strip()

    if len(url) > MAX_URL_LENGTH:
        return error("Please enter a shorter URL.", 400)
       
    if not "://" in url:
        url = "http://" + url
    
    try:
        url_split = urlparse(url)
        # Reading url_split.port here raises an exception if malformed, avoiding errors later
        _ = url_split.port
    except ValueError:
        return error("Please enter a valid URL.", 400)

    if (not url_split.netloc) or (url_split.scheme not in ALLOWED_SCHEMES):
        return error("Please enter a valid URL.", 400)
    
    code = insert_entry(url) 
    conn.commit()

    if not code:
        return error("Something went wrong.", 503)

    return jsonify({"short_url": code})


@app.route("/<code>")
def direct(code):
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM url_map WHERE shortened IS ?", (code,))
    fetch = cursor.fetchone()

    if fetch:
        url = fetch[0]
        return redirect(url)
    else:
        return error("This URL isn't in our system.", 404)

def main():
    app.run()

if __name__ == "__main__":
    main()
