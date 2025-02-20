from pytubefix import YouTube
from discord.ext import commands
import discord
import os
import scripts.ytmp3 as ytmp3
import asyncio
import random
from scripts.SongOfTheDay import SpotifySong
from scripts.helpers.vid_helpers import getVidUrl, getTempFile
from moviepy import vfx, VideoFileClip
import tempfile
import urllib.parse
#import wavelink

#TODO: for files that go over upload limit, upload to temp file hosting service and send link

class SpeedFlags(commands.FlagConverter):
    speed: float = commands.flag(default=1.0)
    size: float = commands.flag(default=1.0)
    url: str = commands.flag(default=None)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def vc(url):
        yt = YouTube(url)
        strUrl = yt.streams.get_audio_only().url
        return strUrl
    
    @commands.command(name="mp3", description="takes a youtube url and sends the audio as an mp3")
    async def mp3(self, ctx: commands.Context, url):
        async with ctx.typing():
            try:
                file_path = await asyncio.to_thread(ytmp3.yt2mp3, url)
                print(f"file path: {file_path}")

            except Exception as e:
                print(f"error downloading: {e}")
                await ctx.send(f"error downloading: {e}")
            
            print(f"trying {file_path}")
            if file_path:
                await ctx.send("download successful")

                if await ctx.send(file=discord.File(file_path)):
                    print("valid upload size")
                    #await ctx.send("valid upload size")
                else:
                    print("file too large")
                    ctx.send("file too large")
            tmp = ytmp3.yttitle
            os.remove(os.getcwd() + "\\" + tmp + ".mp3")


    @commands.command(name="mp4", description="takes a youtube url and sends video as mp4")
    async def mp4(self, ctx: commands.Context, url):
        async with ctx.typing():
            try:
                file_path = await asyncio.to_thread(ytmp3.yt2mp4, url)
                print(f"file path: {file_path}")

            except Exception as e:
                    print(f"error downloading: {e}")
                    await ctx.send(f"error downloading: {e}")
            
            if file_path:
                await ctx.send("download successful")
                
                if await ctx.send(file=discord.File(file_path)):
                    print("valid upload size")
                    #await ctx.send("valid upload size")
                else:
                    print("file too large")
                    await ctx.send("file too large")
            tmp = ytmp3.yt4title
            os.remove(os.getcwd() + "\\" + tmp + ".mp4")

    
    #TODO: search feature
    @commands.command(aliases=["sotd","spotifysong"], description="sends a random song from a spotify album/playlist")
    async def spotify(self, ctx: commands.Context, url):
        try:
            song, apiResult = await SpotifySong(url)
        except Exception as e:
            print(e)
            return
        # logic to choose between album and playlist
        if apiResult == "playlist":
            songItems = song['items']
            ranSongChoice = random.choice(songItems)
            choice = ranSongChoice['track']['external_urls']['spotify']
            if choice:
                print(choice)
            else:
                print("no choice found")
            await ctx.send(choice)
        elif apiResult == "album":
            songItems = song['items']
            ranSongChoice = random.choice(songItems)
            choice = ranSongChoice['external_urls']['spotify']
            await ctx.send(choice)
        else:
            print("input is neither playlist nor album")


    @commands.command(description="usage: >edit speed: <float> size: <float> url: <string>")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def edit(self, ctx: commands.Context, *, flags: SpeedFlags):
        # Default speed validation
        if flags.speed < 0.1:
            print(f"value of speed ({flags.speed}) too low, setting to 0.1")
            flags.speed = 0.1
        elif flags.speed > 40:
            print(f"value of speed ({flags.speed}) is too high, setting it to 40")
            flags.speed = 40
        if flags.size > 1:
            flags.size = 1     
        
        async with ctx.typing():
            # Retrieve video URL
            vidUrl, vidName = await getVidUrl(ctx, flags.url)
            
            # download the video into a temporary file
            #tmp_video_path = await getTempFile(self.bot.session, vidUrl)

            async with self.bot.session.get(vidUrl) as attach:
                if attach.status != 200:
                    print("problem downloading")
                    return

                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video_file:
                        tmp_video_file.write(await attach.read())
                        tmp_video_path = tmp_video_file.name
                        print(f"Temporary video file created: {tmp_video_path}")
                except Exception as e:
                    print(f"Error creating temporary video file: {e}")
                    return
            
            # process video
            try:
                with VideoFileClip(tmp_video_path) as clip:
                    with clip.with_speed_scaled(float(flags.speed)) as editClip:
                        #editClip = editClip.fx(vfx.FadeIn)
                        editClip = editClip.resized(flags.size)
                        
                        # delete is false because otherwise the temp file would be deleted before
                        # it could be accessed
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output_file:
                            tmp_output_path = tmp_output_file.name
                            editClip.write_videofile(tmp_output_path, audio_codec="aac")
                            print(f"Output video written to temporary file: {tmp_output_path}")
            except Exception as e:
                print(f"Error processing video: {e}")
                os.remove(tmp_video_path)
                return
            
            # send video
            try:
                await ctx.send(file=discord.File(tmp_output_path, f"{vidName}_output.mp4"))
            except Exception as e:
                print(f"Problem uploading video: {e}")
            
            os.remove(tmp_video_path)
            os.remove(tmp_output_path)


    #@commands.command()
    #async def resolution():
    #    pass


    #@commands.command()
    #async def ytp(self, ctx: commands.Context)
    #    pass
    



    #@commands.command()
    #async def vcsong(ctx, url):
        #channel = ctx.author.voice.channel
        #await channel.connect()
        
    #    streamUrl = commands.vcmusic.vc(url)
    #    print(streamUrl[:20])
        #await ctx.send(streamUrl)
    #    try:
    #        node: wavelink.Node = wavelink.Node(uri=config.lavalink_uri, password=config.lavalink_password, client=bot)
    #    except Exception as e:
    #        print(f"exception   _  adfasdkf{e}")
    #    print("wavelink node initialized")
    #    await wavelink.Pool.connect(nodes=[node], cache_capacity=100)

        #vcPlayer = await wavelink.Player(client=bot, nodes=wnode)

        #await wavelink.Pool.close()
        
    # @button
        

async def setup(bot):
    await bot.add_cog(Music(bot))