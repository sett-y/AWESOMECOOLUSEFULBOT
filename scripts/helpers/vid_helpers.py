#from moviepy import VideoFileClip, vfx
from discord.ext import commands
import urllib.parse
import os
import tempfile


#TODO: helper functions that check video url, parse, then save and return temp vid path

async def getVidUrl(ctx: commands.Context, url=None):
    if ctx.message.attachments:
        if ctx.message.attachments[0].filename.lower().endswith(('mp4', 'webm', 'mov')):
            vidUrl = ctx.message.attachments[0].url
            vidName = ctx.message.attachments[0].filename
            print(vidName)
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
            return
    else:
        print("invalid video")
        return
    
    return vidUrl, vidName

async def getTempFile(session, vidUrl):
    async with session.get() as attach:
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

        return tmp_video_path
    
