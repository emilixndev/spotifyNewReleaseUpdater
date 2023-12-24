import json
import os
import time

import dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session, url_for

PlaylistToLookUpName = "ToAddInGymPlaylist"
PlaylistToAddIn = "Gym - Hard"

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
    playlistToAddIn = ""
    tracksToAdd = []
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")
    artisteToLookup = []
    sp = spotipy.Spotify(auth=token_info)
    current_playlists = sp.current_user_playlists()['items']
    print("PLAYLISTS")
    print(current_playlists)
    for playlist in current_playlists:
        if playlist['name'] == PlaylistToLookUpName:
            print("Playlist to search in found")
            playlistItems = sp.playlist_items(playlist['id'])['items']

            for item in playlistItems:
                artisteToLookup.append(item['track']['artists'][0]['id'])
        if playlist['name'] == PlaylistToAddIn:
            playlistToAddIn = playlist

    print("ARTISTE TO LOOKUP TO")
    print(artisteToLookup)

    for artisteid in artisteToLookup:

        singles = sp.artist_albums(artisteid, limit=2, album_type='single')
        print("start looking for singles ")
        for single in singles['items']:

            # if release date is today
            if single['release_date'] == time.strftime("%Y-%m-%d"):
            # if (single['release_date'] == "2023-12-22"):
                print("Single found today")

                tracksToAdd.append(sp.album(single['id'])['tracks']['items'][0]['uri'])

                print(single['name'])
        # same with albums
        albums = sp.artist_albums(artisteid, limit=2, album_type='album')
        for album in albums['items']:
            # if release date is today
            if album['release_date'] == time.strftime("%Y-%m-%d"):
                # if album['release_date'] == "2023-11-24":
                print("ALBUM FOUND")
                print(album['name'])

                albumTracks = sp.album_tracks(album['id'])
                for track in albumTracks['items']:
                    print(track['uri'])
                    tracksToAdd.append(track['uri'])
                    sp.playlist_add_items(playlist_id=playlistToAddIn['id'], items=[track['uri']])

    TrackNotDuplicate = []

    for track in tracksToAdd:
        print(track)
        if track not in TrackNotDuplicate:
            TrackNotDuplicate.append(track)
    print("TRACKS TO ADD")
    print(TrackNotDuplicate)
    for finalTrack in TrackNotDuplicate:
        print("ADDING TRACK")
        sp.playlist_add_items(playlist_id=playlistToAddIn['id'], items=[finalTrack])

    # sp.playlist_add_items(playlist_id=playlistToAddIn['id'], items=[album['tracks']['items']['uri']])
    printTest()
    return "OAUTH SUCCESSFUL"


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        return redirect(url_for('login', external=True))
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
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
