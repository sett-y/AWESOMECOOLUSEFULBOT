import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from scripts.config import spotify_client_id, spotify_client_secret

async def SpotifySong(url):
    # logic to decide between song and album

    auth_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                            client_secret=spotify_client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    userPlaylist = sp.playlist_items(playlist_id=url, additional_types="track")

    return userPlaylist