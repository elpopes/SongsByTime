from flask import Flask, request, redirect, session, render_template, url_for
import requests
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, FLASK_SECRET_KEY

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
REDIRECT_URI = 'http://localhost:8888/callback'

@app.route('/')
def home():
    return render_template('index.html')  

@app.route('/login')
def login():
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={SPOTIFY_CLIENT_ID}&scope=user-library-read user-read-email&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code provided", 400

    auth_token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }
    try:
        post_request = requests.post(auth_token_url, data=data)
        post_request.raise_for_status()  # Raises an HTTPError for bad responses
        response_data = post_request.json()
        access_token = response_data.get('access_token')
        if access_token:
            session['access_token'] = access_token  # Store access token in session
            return redirect(url_for('search_page'))  # Redirect to search page
        else:
            return "Error: Access token not received", 500
    except requests.RequestException as e:
        return str(e), 500

@app.route('/search_page')
def search_page():
    return render_template('search.html')  

@app.route('/search')
def search_songs():
    if 'access_token' not in session:
        return "Access token is missing, please login again", 401
    access_token = session['access_token']

    min_duration_minutes = request.args.get('min_duration_minutes', default=0, type=int)
    min_duration_seconds = request.args.get('min_duration_seconds', default=0, type=int)
    max_duration_minutes = request.args.get('max_duration_minutes', default=0, type=int)
    max_duration_seconds = request.args.get('max_duration_seconds', default=0, type=int)

    min_duration_ms = (min_duration_minutes * 60 + min_duration_seconds) * 1000
    max_duration_ms = (max_duration_minutes * 60 + max_duration_seconds) * 1000

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    query = f"market=US&type=track&limit=50&q=duration_ms:{min_duration_ms} TO {max_duration_ms}"
    response = requests.get(f"https://api.spotify.com/v1/search?{query}", headers=headers)
    tracks = response.json().get('tracks', {}).get('items', [])
    return render_template('results.html', tracks=tracks)

if __name__ == '__main__':
    app.run(port=8888)
