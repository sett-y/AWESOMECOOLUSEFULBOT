#from moviepy import VideoFileClip, vfx
from discord.ext import commands
import urllib.parse
import os
import tempfile
from moviepy import VideoFileClip
from typing import Tuple, Optional


#TODO: helper functions that check video url, parse, then save and return temp vid path

async def getVidUrl(ctx: commands.Context, url=None) -> Tuple[Optional[str], Optional[str]]:
    if ctx.message.attachments:
        if ctx.message.attachments[0].filename.lower().endswith(('mp4', 'webm', 'mov')):
            vidUrl = ctx.message.attachments[0].url
            vidName = ctx.message.attachments[0].filename
            print(vidName)
        else:
            return (None, None)
    elif "http" in ctx.message.content:
        content = ctx.message.content
        httpContent = content.split("http")
        splitContent = httpContent[1].split(" ")
        vidUrl = "http" + splitContent[0]
        vidName = "video"
    elif url:
        parsedUrl = urllib.parse.urlparse(url)
        urlPath = parsedUrl.path
        fileName = os.path.basename(urlPath)
        fileType = os.path.splitext(fileName)[1]
        vidName = os.path.split(fileName)[0]
        print(f"file extension: {fileType}")
        if fileType in ('.mp4', '.mov', '.webm'):
            vidUrl = url
            print(f"success: {vidUrl}")
        else:
            print("epic fail")
            return (None, None)
    else:
        print("invalid video")
        return (None, None)
    
    return vidUrl, vidName

async def checkFileSize(session, vidUrl):
    async with session.head(vidUrl) as response:
        if response.status == 200:
            maxSize = 1024 * 1024 * 12 # 12 mb
            fileSize = int(response.headers.get('Content-Length', 0))
            if fileSize > maxSize:
                return True
            else:
                return False
        else:
            print("could not retrieve file info")
            return True

async def getTempFile(session, vidUrl):
    overMax = await checkFileSize(session, vidUrl)
    if overMax:
        print("over max file size")
        return

    async with session.get(vidUrl) as attach:
        if attach.status != 200:
            print("error while downloading")
            return
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video_file:
                tmp_video_file.write(await attach.read())
                tmp_video_path = tmp_video_file.name
                print(f"Temporary video file created: {tmp_video_path}")
        except Exception as e:
            print(e)
            return

        return tmp_video_path
    
async def getEditedVideoPath(tmp_video_path):
    try:
        with VideoFileClip(tmp_video_path) as editClip:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output_file:
                tmp_output_path = tmp_output_file.name
                editClip.write_videofile(tmp_output_path, audio_codec="aac")
                print(f"Output video written to temporary file: {tmp_output_path}") 
                return tmp_output_path    
    except Exception as e:
        print(f"Error processing video: {e}")
        os.remove(tmp_output_path)
        return