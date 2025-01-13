import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from scripts.config import spotify_client_id, spotify_client_secret

async def SpotifySong(url):
    auth_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                            client_secret=spotify_client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # logic to decide between song and album, should check w/ api instead
    if "playlist" in url:
        userPlaylist = sp.playlist_items(playlist_id=url, additional_types="track")
        return userPlaylist
    
    elif "album" in url:
        userAlbum = sp.album_tracks(album_id=url)
        return userAlbum