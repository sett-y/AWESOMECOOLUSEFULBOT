import spotipy
import traceback
from spotipy.oauth2 import SpotifyClientCredentials
from scripts.config import spotify_client_id, spotify_client_secret

async def SpotifySong(url):
    auth_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                            client_secret=spotify_client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # logic to decide between song and album
    try:
        userPlaylist = sp.playlist_items(playlist_id=url, additional_types="track")
        return userPlaylist, "playlist"
    except Exception as e:
        print("type is not playlist")
        if e:
            print("exception found:")
            print(f"{e}\n{traceback.print_exc}")
    
    try:
        userAlbum = sp.album_tracks(album_id=url)
        return userAlbum, "album"
    except Exception as e:
        print("type is not album or playlist")
        if e:
            print("exception found:")
            print(f"{e}\n{traceback.print_exc()}")