# URL Shortener

A small URL shortener built with Flask and SQLite. Paste a long link into the web page and get back a short one that redirects to the original. The same functionality is available as a JSON API.

## Features

- Shorten any `http` or `https` URL from a simple web page
- Bare domains such as `example.com` are accepted and given an `http://` prefix
- Short codes are random and URL-safe (7 characters)
- Links are stored in SQLite and survive server restarts
- Input validation rejects non-string values, unsupported schemes, malformed URLs and over-long URLs

## Tech stack

- Python and Flask
- SQLite
- Plain HTML and JavaScript on the front end
- [Pico CSS](https://picocss.com/) for styling

## Setup and run

Developed and tested on Python 3.13.

```bash
git clone https://github.com/james-unsworth/URL_shortener
cd URL_shortener
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open <http://127.0.0.1:5000>. The database file `url_map.db` is created automatically on first run.

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | The web page |
| `POST` | `/shorten` | Create a short link |
| `GET` | `/<code>` | Redirect to the original URL |

### `POST /shorten`

Request body:

```json
{"url": "https://example.com/some/long/path"}
```

Success (`200`):

```json
{"short_url": "Hay3tfs"}
```

`short_url` is the short code. The full short link is `<host>/<code>`, for example `http://127.0.0.1:5000/Hay3tfs`. The web page builds this link from `window.location.origin`.

Errors return a JSON body with a single `err_msg` field. The HTTP status code is the success/failure signal.

### `GET /<code>`

Redirects to the stored URL. If the code does not exist it returns `404`.

## Design decisions

**Collisions:** The code is the table's primary key, so inserting a duplicate raises `sqlite3.IntegrityError`. The server catches it and retries with a new code up to 50 times, then returns `503`. Collisions should only become likely at roughly a million stored links.

**Validation.** The checks run in this order: body is a JSON object, `url` is a string, whitespace is trimmed, length is at most 2048, `http://` is added if no `://` is present, the URL parses without error (including its port), it has a host, and its scheme is `http` or `https`. The scheme allowlist rejects values such as `javascript:` and `ftp:`.

**Errors.** One helper builds every error response, so all errors have the same JSON format. The front end reads the HTTP status and shows `err_msg` directly.

**Front end safety.** The page builds the result link with DOM methods and `textContent` rather than `innerHTML`, so server data is never interpreted as HTML.

## Known limitations

- **Open redirect:** The service redirects to any stored `http`/`https` URL, so it could be used to disguise links in phishing. There is no blocklist.
- **No rate limiting or authentication:**
- **Single shared database connection.** The app uses one SQLite connection with `check_same_thread=False` and no locking. This is fine for local use only.
- **Development server only.** It runs with Flask's built-in server, not a production server.
- **Minimal URL validation by design.** For example, `http://123` is accepted as a host, and spaces inside a host are not rejected. The URL is not fetched to check that it exists.
- **No request body size limit** beyond the 2048-character URL cap
- **Generic network error.** A non-JSON server error shows the same "couldn't reach the server" message as a network failure.

## Possible improvements

- Automated tests with `pytest` and Flask's test client
- Rate limiting and a blocklist of unsafe domains
- A production WSGI server and one database connection per request

## Project structure

```
URL_shortener/
├── app.py              # Flask app: routes, validation, database access
├── requirements.txt
├── templates/
│   └── index.html      # Web page
└── static/
    ├── script.js       # Calls /shorten and shows the result or error
    └── style.css       # Small layout tweaks on top of Pico CSS
```
