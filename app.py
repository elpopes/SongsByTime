from flask import Flask, request, redirect
import requests
import os
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

app = Flask(__name__)

REDIRECT_URI = 'http://localhost:8888/callback'

@app.route('/')
def login():
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={SPOTIFY_CLIENT_ID}&scope=user-library-read&redirect_uri={REDIRECT_URI}"
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
            return f"Access token: {access_token}"
        else:
            return "Error: Access token not received", 500
    except requests.RequestException as e:
        return str(e), 500

@app.route('/search')
def search_songs():
    # Receive duration in minutes and seconds from user
    min_duration_minutes = request.args.get('min_duration_minutes', default=0, type=int)
    min_duration_seconds = request.args.get('min_duration_seconds', default=0, type=int)
    max_duration_minutes = request.args.get('max_duration_minutes', default=0, type=int)
    max_duration_seconds = request.args.get('max_duration_seconds', default=0, type=int)

    # Convert durations to milliseconds
    min_duration_ms = (min_duration_minutes * 60 + min_duration_seconds) * 1000
    max_duration_ms = (max_duration_minutes * 60 + max_duration_seconds) * 1000

    access_token = request.args.get('access_token') 

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    query = f"market=US&type=track&limit=50&q=duration_ms:{min_duration_ms} TO {max_duration_ms}"
    response = requests.get(f"https://api.spotify.com/v1/search?{query}", headers=headers)
    tracks = response.json()

    return tracks


if __name__ == '__main__':
    app.run(port=8888)
