import requests
import time

class SpotifyAPI:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://api.spotify.com/v1/"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0

    def get_auth_url(self):
        scope = "user-top-read playlist-modify-private playlist-read-private"
        return f"{self.auth_url}?client_id={self.client_id}&response_type=code&scope={scope}&redirect_uri={self.redirect_uri}"

    def exchange_code_for_token(self, code):
        req_body = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(self.token_url, data=req_body)
        token_info = response.json()
        self.access_token = token_info['access_token']
        self.refresh_token = token_info.get('refresh_token')
        self.expires_at = int(time.time()) + token_info['expires_in']

    def refresh_access_token(self):
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(self.token_url, data=req_body)
        token_info = response.json()
        self.access_token = token_info['access_token']
        if 'expires_in' in token_info:
            self.expires_at = int(time.time()) + token_info['expires_in']

    def get_user_id(self):
        response = requests.get(f"{self.base_url}me", headers={"Authorization": f"Bearer {self.access_token}"})
        return response.json().get("id")

    def get_top_tracks(self):
        response = requests.get(f"{self.base_url}me/top/tracks?limit=50&time_range=short_term", 
                                headers={"Authorization": f"Bearer {self.access_token}"})
        return [track["id"] for track in response.json().get("items", [])]

    def get_playlists(self, user_id):
        response = requests.get(f"{self.base_url}users/{user_id}/playlists", 
                                headers={"Authorization": f"Bearer {self.access_token}"})
        return response.json().get("items", [])

    def create_playlist(self, user_id, playlist_name):
        response = requests.post(
            f"{self.base_url}users/{user_id}/playlists",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"name": playlist_name, "public": False}
        )
        return response.json()["id"]

    def update_playlist(self, playlist_id, track_ids):
        requests.put(
            f"{self.base_url}playlists/{playlist_id}/tracks",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"uris": [f"spotify:track:{track_id}" for track_id in track_ids]}
        )
