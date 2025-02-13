import spotipy
import traceback
from spotipy.oauth2 import SpotifyClientCredentials
from scripts.config import spotify_client_id, spotify_client_secret

async def SpotifySong(url):
    auth_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                            client_secret=spotify_client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    spotify_id = url.split('/')[-1].split('?')[0]

    # logic to decide between song and album
    try:
        userPlaylist = sp.playlist_items(playlist_id=spotify_id, additional_types="track")
        return userPlaylist, "playlist"
    except Exception as e:
        print("type is not playlist")
        print(f"exception found: {e}")
        traceback.print_exc()
    
    try:
        userAlbum = sp.album_tracks(album_id=spotify_id)
        return userAlbum, "album"
    except Exception as e:
        print("type is not album or playlist")
        print(f"exception found: {e}")
        traceback.print_exc()

    return None, "unknown"