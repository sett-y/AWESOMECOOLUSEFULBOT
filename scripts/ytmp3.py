from pytubefix import YouTube
import os
from typing import Optional

yttitle = ""
yt4title = ""

def yt2mp3(url) -> Optional[str]:
    # is there a point to this global
    global yttitle
    output_path = os.getcwd()

    #if "https://www.youtube.com" not in url:
    #    url = "https://www.youtube.com/v=?" + url

    url = url.strip()
    vidInfo = YouTube(url, 'WEB')
    san = vidInfo.title
    invalidChars = "<>:/\\?*|"
    for char in invalidChars:
        san = san.replace(char, "_")
    filename = san + ".mp3"
    yttitle = san
    
    mp3 = vidInfo.streams.get_audio_only()

    if mp3:
        print("stream success")
        download = mp3.download(output_path=output_path, filename="audio.mp3")
    else:
        print("no valid stream")
        return None

    if not download:
        print("error while downloading")
        return None

    newfilepath = os.path.join(output_path, filename)
    if os.path.exists(newfilepath):
        os.remove(newfilepath)
    
    try:
        os.rename(download, newfilepath)
    except OSError as e:
        print(f"rename failed: {e}")
        # in case rename fails
        os.remove(download)
        return None

    print(f"downloaded {url}")
    print(f"output path: {output_path}")

    return newfilepath


def yt2mp4(url) -> Optional[str]:
    global yt4title
    output_path = os.getcwd()

    url = url.strip()
    vidInfo = YouTube(url, 'WEB')
    invalidChars = "<>:/\\?*|"
    san = vidInfo.title
    for char in invalidChars:
        san = san.replace(char, "_")

    filename = san + ".mp4"
    yt4title = san
    
    #mp4 = vidInfo.streams.get_highest_resolution() #filter(file_extension="mp4")#.first()
    mp4 = vidInfo.streams.filter(file_extension="mp4").first()
    
    if mp4:
        print("stream success")
        download = mp4.download(output_path=output_path, filename = "vid.mp4")
    else:
        print("no valid stream")
        return None
    
    if not download:
        print("error while downloading")
        return None

    newfilepath = os.path.join(output_path, filename)
    if os.path.exists(newfilepath):
        print("path exists")
        os.remove(newfilepath)
    
    try:
        os.rename(download, newfilepath)
    except Exception as e:
        print(f"rename failed: {e}")
        os.remove(download)
        return None

    print(f"downloaded {url}")
    print(f"output path: {output_path}")

    return newfilepath