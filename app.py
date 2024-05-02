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
    auth_token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }
    post_request = requests.post(auth_token_url, data=data)
    response_data = post_request.json()
    access_token = response_data.get('access_token')
    return f"Access token: {access_token}"

if __name__ == '__main__':
    app.run(port=8888)
