import json
import os
import time

import dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session, url_for

dotenv.load_dotenv()
app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
app.secret_key = 'krksjdfkjsdkfjksdj4454kjsdfkjs'

TOKEN_INFO = 'token_info'


@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('savePlaylists', external=True))


@app.route('/savePlaylists')
def savePlaylists():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")

    sp = spotipy.Spotify(auth=token_info)
    current_playlists = sp.current_user_playlists()['items']
    for playlist in current_playlists:
        if(playlist['name'] == 'Gym - Hard'):
            print(playlist)
            # Get Json formated
            text = json.dumps(playlist, sort_keys=True, indent=4)
            print(text)

    return ("OAUTH SUCCESSFUL")


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        return redirect(url_for('login', external=True))
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info['access_token']


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        redirect_uri=url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private')


app.run(debug=True)
