from discord.ext import commands, tasks
import discord
import scripts.catFacts as catFacts
import scripts.scraper as scraper
import PIL
import random
import datetime
from scripts.robloxscrape import get_gamedata
from scripts.YoutubeSearch import youtubeSearch
from scripts.SongOfTheDay import SpotifySong


class Scrapers(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.command(aliases=["catfact","cat"], description="displays a random cat fact")
    async def catFact(self, ctx: commands.Context):
        #TODO: delete this after get_fact is done
        await ctx.send("loading cat fact...")
        try:
            catFact = await catFacts.get_fact()
            await ctx.send(catFact)
        except:
            print("error while scraping page")

    @commands.command(description="displays info about dota match")
    async def display_match(self, ctx: commands.Context): # add url back to params
        #await ctx.send("fetching match...")
        #html = await scraper.call_scraper("get_match_info", url)

        thumbnail = discord.File("images/dotabuff.png", filename="dotabuff.png")
        embed = discord.Embed(title="bruh")
        embed.add_field(name="test 1", value="tasdfdfjlasdjf")
        embed.add_field(name="test 2", value="aldfjaldskjfd", inline=False)
        embed.add_field(name="test 3", value="\nadjfdfj", inline=False)
        embed.add_field(name="inline test", value="this is inline", inline=True)
        embed.add_field(name="inline test 2", value="this is also inline", inline=True)
        embed.set_thumbnail(url="attachment://dotabuff.png")
        embed.set_author(name=f"requested by {ctx.author.name}")

        await ctx.send(file=thumbnail, embed=embed)

        """await ctx.send(html[0])
        for h in html[1]:
            await ctx.send(h)
            asyncio.sleep(0.2)
        await ctx.send(html[2])
        for h in html[3]:
            await ctx.send(h)
            asyncio.sleep(0.2)"""

        #PIL code here
        
    @commands.command(description="displays info about user dotabuff profile")
    async def display_profile(ctx: commands.Context, url):
        await ctx.send("fetching profile...")
        html = await scraper.call_scraper("parse_profile", url)
        
        #for h in html:
            #await ctx.send(h)

    @commands.command(aliases=['rg'], description="video game 4 the gamily")
    async def robloxgame(self, ctx: commands.Context, id = ''):
        await ctx.send("Checking 4 Game!")
        async with ctx.channel.typing():
            data = await get_gamedata(id)
        if data == 1:
            await ctx.send("Game not found!")
        embed = discord.Embed(title='roblo game')
        embed.add_field(name='Title', value=data[0])
        embed.add_field(name="Player Count", value=data[1])
        embed.add_field(name="Link", value=f'[link]({data[3]})')
        embed.add_field(name="Description", value=data[4])
        embed.set_thumbnail(url=data[2]) 
        await ctx.send(embed=embed)

    @commands.command(aliases=["yt","youtubesearch","ytsearch"], description="searches and displays the top 5 youtube search results for a topic")
    async def youtube(self, ctx: commands.Context, *, searchTerm):
        async with ctx.channel.typing():
            searchTerm = "https://www.youtube.com/results?search_query=" + searchTerm
            searchTerm = searchTerm.replace(" ","+")
            #await ctx.send(searchTerm)
            thumbnails = await youtubeSearch(searchTerm)
            if thumbnails:
                print("success")
                for img in thumbnails:
                    await ctx.send(img)
            else:
                print("epic fail")
                await ctx.send(f"results scraped: {len(thumbnails)}")
            
        embed = discord.Embed(title="youtube")
        embed.set_thumbnail(url="https://i.ytimg.com/vi/b0zE0jrAUXo/hq720.jpg?sqp=-oaymwEnCNAFEJQDSFryq4qpAxkIARUAAIhCGAHYAQHiAQoIGBACGAY4AUAB&rs=AOn4CLCZVNqjADBwRPMkz8T7nzYgeaE59A")
        embed.set_image(url="https://i.ytimg.com/vi/b0zE0jrAUXo/hq720.jpg?sqp=-oaymwEnCNAFEJQDSFryq4qpAxkIARUAAIhCGAHYAQHiAQoIGBACGAY4AUAB&rs=AOn4CLCZVNqjADBwRPMkz8T7nzYgeaE59A")
        
        await ctx.send(embed=embed)
        
    @commands.command(aliases=["sotd","spotifysong"], description="sends a random song from a spotify album")
    async def spotify(self, ctx: commands.Context, url):
        song = await SpotifySong(url)
        # logic to choose between album and playlist

        songItems = song['items']

        ranSongChoice = random.choice(songItems)
        choice = ranSongChoice['track']['external_urls']['spotify']

        await ctx.send(choice)

    @tasks.loop(time=datetime.time(hour=5, minute=41))
    async def dailySong(self, ctx: commands.Context):
        channel = self.bot.get_channel(684575538957910055)
        song = await SpotifySong("https://open.spotify.com/playlist/04mZkGQA7QgVt3SPHuob76?si=AYE-9WXlSUOaixoMER3SZw")
        songItems = song['items']

        ranSongChoice = random.choice(songItems)
        choice = ranSongChoice['track']['external_urls']['spotify']

        await channel.send(choice)


def setup(bot):
    bot.add_cog(Scrapers(bot))