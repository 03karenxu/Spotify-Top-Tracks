#!/usr/bin/python3

import os
import time
from dotenv import load_dotenv
from flask import Flask, redirect, request, jsonify, session, url_for
from spotifyapi import SpotifyAPI  # Importing the SpotifyAPI class

# load .env variables
load_dotenv()

# init Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# global variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT = os.getenv("REDIRECT")
BASE_URL = "https://api.spotify.com/v1/"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
PLAYLIST_NAME = "last month's top songs :-)"

@app.route('/')
def login():
    # send to spotify authorization page
    scope = "user-top-read playlist-modify-private playlist-read-private"
    auth_url = f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&scope={scope}&redirect_uri={REDIRECT}"

    return redirect(auth_url)

@app.route('/callback')
def callback():
    # check if code was received from server
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    if 'code' in request.args:  # exchange code for access token
        spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET, REDIRECT)
        spotify_api.exchange_code_for_token(request.args['code'])
        
        # Store token info in session
        session['access_token'] = spotify_api.access_token
        session['expires_at'] = spotify_api.expires_at
        
        return redirect(url_for('top_tracks'))

@app.route('/top_tracks')
def top_tracks():
    # get access token
    token = session.get('access_token')

    # check if needs to be refreshed
    is_expired = int(time.time()) >= session.get('expires_at', 0) - 60
    if not token or is_expired:
        spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET, REDIRECT)  # Use the imported SpotifyAPI class
        spotify_api.access_token = token  # Update the access token
        spotify_api.refresh_access_token()  # Use the class method to refresh the token
        token = spotify_api.access_token
        session['access_token'] = token
        session['expires_at'] = spotify_api.expires_at
    
    spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET, REDIRECT)  # Use the imported SpotifyAPI class
    spotify_api.access_token = token  # Update the access token
    user_id = spotify_api.get_user_id()  # Use the SpotifyAPI methods
    top_tracks = spotify_api.get_top_tracks()
    
    # Get or create playlist
    playlists = spotify_api.get_playlists(user_id)
    playlist_id = None
    for playlist in playlists:
        if playlist["name"] == PLAYLIST_NAME:
            playlist_id = playlist["id"]
            break
    
    if not playlist_id:
        playlist_id = spotify_api.create_playlist(user_id, PLAYLIST_NAME)
    
    # Update playlist with top tracks
    spotify_api.update_playlist(playlist_id, top_tracks)
    
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return "Playlist updated succesfully!<br>˚ʚ♡ɞ˚"

if __name__ == "__main__":
    app.run(debug=True)





