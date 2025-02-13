from pytubefix import YouTube
from discord.ext import commands
import discord
import os
import scripts.ytmp3 as ytmp3
import asyncio
import random
from scripts.SongOfTheDay import SpotifySong
from moviepy import vfx, VideoFileClip
#import wavelink

#TODO: for files that go over upload limit, upload to temp file hosting service and send link

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def vc(url):
        yt = YouTube(url)

        strUrl = yt.streams.get_audio_only().url
        
        return strUrl
    
    @commands.command(name="mp3", description="takes a youtube url and sends the audio as an mp3")
    async def mp3(self, ctx: commands.Context, url):
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

    @commands.command()
    async def speed(self, ctx: commands.Context, url=None):
        if ctx.message.attachments:
            pass
        elif url:
            pass

    
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