from discord.ext import commands, tasks
import discord
import PIL
import random
import datetime
import io
import traceback
from bs4 import BeautifulSoup
import scripts.catFacts as catFacts
import scripts.scraper as scraper
from scripts.robloxscrape import get_gamedata
from scripts.YoutubeSearch import youtubeSearch
from scripts.SongOfTheDay import SpotifySong
from scripts.TwitterBot import postMessage, getLastPost
from scripts.helpers.db_helpers import return_guild_emoji


class Scrapers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.bot.add_listener(self.on_raw_reaction_add, 'on_raw_reaction_add')
        self.reactionsNeeded = 1
        # add dict with guild ids for keys that tracks the reaction threshhold

    @commands.command(aliases=["felinefact","cat"], description="displays a random cat fact")
    async def catfact(self, ctx: commands.Context):
        try:
            async with ctx.channel.typing():
                catFact = await catFacts.get_fact()
                await ctx.send(catFact)
        except:
            print("error while scraping page")
            await ctx.send("error while scraping page")

    @commands.command(description="displays info about dota match")
    async def display_match(self, ctx: commands.Context): # add url back to params
        #await ctx.send("fetching match...")
        #html = await scraper.call_scraper("get_match_info", url)

        thumbnail = discord.File("files/images/dotabuff.png", filename="dotabuff.png")
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

    #TODO: cmd to display latest post
    @commands.command(aliases=["bsky","bluesky","latestpost"], description="fetches last bsky post")
    async def latest(self, ctx: commands.Context):
        post = await getLastPost()
        await ctx.send(post)
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # maybe have list of messages to ignore once react threshold is reached

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reactions = message.reactions

        react_emoji = await return_guild_emoji(payload.guild_id, self.bot.cur, "🚎")

        #if message.author.id == self.bot.user.id:
        #    return

        if str(payload.emoji) == react_emoji:
            for reaction in reactions:
                if str(reaction.emoji) == react_emoji:
                    if reaction.count == self.reactionsNeeded:
                        print("posting message")

                        if message.attachments:# attachment in msg
                            attachment = message.attachments[0]
                            async with self.bot.session.get(attachment.url) as mediaFile:
                                if mediaFile.status == 200:
                                    data = io.BytesIO(await mediaFile.read())
                                    with open(f"files/images/{attachment.filename}","wb") as file:
                                        file.write(data.getbuffer())

                            if attachment.filename.lower().endswith(('png','jpg','jpeg','webp','bmp')):
                                # file is an image
                                img = f"files/images/{attachment.filename}"
                                if message.content:
                                    content = f"{message.content} - {message.author.name}"
                                    await postMessage(message=content, attachment=img, username=message.author.name)
                                else:
                                    await postMessage(attachment=img, username=message.author.name)

                            elif attachment.filename.lower().endswith(('mp4','webm','mov','gif')):
                                # file is a video
                                video = f"files/images/{attachment.filename}"
                                #await postMessage(attachment=video)
                                if message.content:
                                    content = f"{message.content} - {message.author.name}"
                                    await postMessage(message=message.content, attachment=video, username=message.author.name)
                                else:
                                    await postMessage(attachment=video, username=message.author.name)

                        else:# no url or attachment in msg    
                            await postMessage(f"{message.content} - {message.author.name}")
                        # end loop since correct emoji found
                        break

                        """elif message.content.startswith("http"):# url in msg
                            async with self.bot.session.get(message.content) as mediaFile:
                                if mediaFile.status == 200:
                                    data = io.BytesIO(await mediaFile.read())
                                    with open(f"files/images/{attachment.filename}","wb") as file:
                                        file.write(data.getbuffer())
                            
                            #if attachment"""

    @tasks.loop(time=datetime.time(hour=22, minute=0))
    async def dailysong(self, ctx: commands.Context):
        channel = self.bot.get_channel(684575538957910055)
        # unpacking because SpotifySong returns a tuple
        song, dummyVal = await SpotifySong("https://open.spotify.com/playlist/04mZkGQA7QgVt3SPHuob76")
        songItems = song['items']

        ranSongChoice = random.choice(songItems)
        choice = ranSongChoice['track']['external_urls']['spotify']

        await channel.send(choice)

    @dailysong.before_loop
    async def before_dailysong(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def testdaily(self, ctx: commands.Context):
        try:
            await self.dailysong(self)
        except Exception as e:
            #tb = traceback.extract_tb(e.__traceback__)
            #lineNum = tb[-1].lineno
            print(f"exception {e} happened at line {traceback.print_exc}")
        print("daily task tested")

    @commands.command(aliases=["apod","astronomy"], description="Astronomy Picture of the Day")
    async def nasa(self, ctx: commands.Context):
        embed = discord.Embed(title="Astronomy Picture of the Day", color=discord.Color.blurple())

        apod_url = "https://apod.nasa.gov/apod/"
        try:
            async with self.bot.session.get(apod_url) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                iframe = soup.find("iframe")
                image = soup.find("img")

                # scrape text
                description = soup.select('p > b')
                parent = description[0]
                desc = parent.parent
                description_split = desc.text.split(sep="Tomorrow's")
                description_split_newline = description_split[0].replace('\n',' ')
                
                embed.add_field(name="Website:", value="https://apod.nasa.gov/apod/",
                                inline=False)
                embed.add_field(name="Description:",
                                value=description_split_newline)
                thumbnail = discord.File(fp="files/images/apod.png", filename="apod.png")
                embed.set_thumbnail(url="attachment://apod.png")

                # check if they exist
                if iframe is not None:
                    print("looking for youtube link")
                    await ctx.send(embed=embed, file=thumbnail)
                    await ctx.send(iframe['src'])
                    print("link sent")
                elif image is not None:
                    print("looking for image src")
                    await ctx.send(embed=embed, file=thumbnail)
                    await ctx.send(apod_url + image['src'])
                    print("image sent")
                else:
                    print("source is of a different media type")   
                
        except Exception as e:
            print(e)
            

async def setup(bot):
    await bot.add_cog(Scrapers(bot))