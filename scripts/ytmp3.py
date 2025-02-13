from pytubefix import YouTube
import os

yttitle = ""
yt4title = ""

def yt2mp3(url) -> str:
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
    download = mp3.download(output_path=output_path)

    newfilepath = os.path.join(output_path, filename)
    if os.path.exists(newfilepath):
        os.remove(newfilepath)
    os.rename(download, newfilepath)

    print(f"downloaded {url}")
    print(f"output path: {output_path}")

    return newfilepath


def yt2mp4(url) -> str:
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
    else:
        print("no valid stream")

    
    if mp4:
        download = mp4.download(output_path=output_path, filename = "vid.mp4")
    else:
        print("no stream found")

    newfilepath = os.path.join(output_path, filename)
    if os.path.exists(newfilepath):
        print("path exists")
        os.remove(newfilepath)
    os.rename(download, newfilepath)

    print(f"downloaded {url}")
    print(f"output path: {output_path}")

    return newfilepath