from pytubefix import YouTube
from discord.ext import commands
import discord
import os
import scripts.ytmp3 as ytmp3
import asyncio
import random
from bot import BotType
from scripts.SongOfTheDay import SpotifySong
from scripts.helpers.vid_helpers import getVidUrl, getTempFile
from moviepy import VideoFileClip
from moviepy import vfx
import tempfile
#import wavelink

#TODO: for files that go over upload limit, upload to temp file hosting service and send link

class SpeedFlags(commands.FlagConverter):
    speed: float = commands.flag(default=1.0)
    size: float = commands.flag(default=1.0)
    url: str = commands.flag(default=None)

class Music(commands.Cog):
    def __init__(self, bot: BotType):
        self.bot = bot

    def vc(self, url):
        yt = YouTube(url)
        audio_stream = yt.streams.get_audio_only()
        if audio_stream is None:
            raise ValueError("No audio streams available for this url")
        
        strUrl = audio_stream.url
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
                return
            
            print(f"trying {file_path}")
            if file_path:
                await ctx.send("download successful")

                if await ctx.send(file=discord.File(file_path)):
                    print("valid upload size")
                else:
                    print("file too large")
                    await ctx.send("file too large")
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
                return
            
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

    # filetype checks
    @commands.command(description="usage: >speed speed: <float> size: <float> url: <string>")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def speed(self, ctx: commands.Context, speed: float):
        # Default speed validation
        if speed < 0.1:
            print(f"value of speed ({speed}) too low, setting to 0.1")
            speed = 0.1
        elif speed > 40:
            print(f"value of speed ({speed}) is too high, setting it to 40")
            speed = 40    
        
        async with ctx.typing():
            # Retrieve video URL
            vidUrl, vidName = await getVidUrl(ctx)
            
            # download the video into a temporary file
            tmp_video_path = await getTempFile(self.bot.session, vidUrl)
            if not tmp_video_path:
                await ctx.send("file over max size")
                print("exiting cmd")
                return
            
            # process video
            try:
                with VideoFileClip(tmp_video_path) as clip:
                    with clip.with_speed_scaled(float(speed)) as editClip:
                        #editClip = editClip.fx(vfx.FadeIn)
                        #editClip = editClip.resized(flags.size)
                        
                        # delete is false because otherwise the temp file would be deleted before
                        # it could be accessed
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output_file:
                            tmp_output_path = tmp_output_file.name
                            editClip.write_videofile(tmp_output_path, audio_codec="aac") # type: ignore
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

    @commands.command(aliases=["res"])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def resolution(self, ctx: commands.Context, res: float):
        if res > 1:
            res = 1.0

        async with ctx.typing():     
            vidUrl, vidName = await getVidUrl(ctx)
            tmp_video_path = await getTempFile(self.bot.session, vidUrl)
            if not tmp_video_path:
                await ctx.send("file over max size")
                print("exiting resolution cmd")
                return

            try:
                with VideoFileClip(tmp_video_path) as clip:
                    with clip.resized(res) as editClip:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output_file:
                            tmp_output_path = tmp_output_file.name
                            editClip.write_videofile(tmp_output_path, audio_codec="aac") # type: ignore
                            print(f"Output video written to temporary file: {tmp_output_path}")
            except Exception as e:
                print(f"Error processing video: {e}")
                os.remove(tmp_video_path)
                os.remove(tmp_output_path)
                return

            await ctx.send(file=discord.File(tmp_output_path, vidName))

        os.remove(tmp_video_path)
        os.remove(tmp_output_path)


    @commands.command()
    async def ytp(self, ctx: commands.Context):
        async with ctx.typing():     
            vidUrl, vidName = await getVidUrl(ctx)
            tmp_video_path = await getTempFile(self.bot.session, vidUrl)
            if not tmp_video_path:
                await ctx.send("file over max size")
                print("exiting resolution cmd")
                return

            try:
                with VideoFileClip(tmp_video_path) as clip:
                    try:
                        clip = clip.with_effects([vfx.TimeMirror()])
                    except Exception as e:
                        print(e)
                        if clip is None: return
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output_file:
                        tmp_output_path = tmp_output_file.name
                        clip.write_videofile(tmp_output_path, audio_codec="aac") # type: ignore
                        print(f"Output video written to temporary file: {tmp_output_path}")
            except Exception as e:
                print(f"Error processing video: {e}")
                os.remove(tmp_video_path)
                os.remove(tmp_output_path)
                return

            await ctx.send(file=discord.File(tmp_output_path, vidName))

        os.remove(tmp_video_path)
        os.remove(tmp_output_path)
    

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