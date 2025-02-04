from discord.ext import commands, bridge
import discord
from scripts.googlescrape import get_search
from scripts.helpers.db_helpers import return_guild_emoji
import random

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def check_guilds(self, ctx: commands.Context):
        g = ""
        for guild in self.bot.guilds:
            g += f"{guild.name}: {guild.id}\n"
        await ctx.send(g)

    @commands.command()
    @commands.is_owner()
    async def leave_guild(self, ctx: commands.Context, id):
        guild = self.bot.get_guild(id)
        guild.leave()
        await ctx.send(f"left guild {guild.name}")

    @commands.command(description="fetches server picture")
    async def servpic(self, ctx: commands.Context):
        if isinstance(ctx, bridge.BridgeApplicationContext):
            await ctx.respond(ctx.guild.icon)
        else:
            await ctx.send(ctx.guild.icon)

    @commands.command(description="displays user join date")
    async def joindate(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title="Join Date")
        embed.add_field(name="", value=f"Account Created: {member.created_at}")
        embed.add_field(name="", value=f"Server Joined: {member.joined_at}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["pfp"], description="sends link to user pfp, can specify user with a ping")
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        pfp = member.avatar.url
        await ctx.send(pfp)

    @commands.command()
    async def delivery_notif(self, ctx: commands.Context, url):
        pass

    @commands.command(description='google search! ! ')
    async def google(self, ctx: commands.Context, *, search_term):
        embed = discord.Embed(title="gooel")
        async with ctx.channel.typing():
            data = await get_search(search_term)

        for i in range(len(data)):
            title = data[i]['title']
            url = data[i]['url']
            site_title = data[i]['site_title']
            embed.add_field(name=f'{site_title}', value=f'[{title}]({url})')
        await ctx.send(embed=embed)

    @commands.command(description="sends list of commands w/ aliases")
    async def aliases(self, ctx: commands.Context):
        commandList = []
        async with ctx.channel.typing():
            for c in self.bot.commands:
                commandList.append(f"{c.name} - {c.aliases}\n")
            cmdList = ''.join(str(c) for c in commandList)
            await ctx.send(cmdList)

    @commands.command(aliases=["wikipedia","wikisearch","randomwiki","rw"], description="sends a random wikipedia page")
    async def wiki(self, ctx: commands.Context):
        async with self.bot.session.get("https://en.wikipedia.org/api/rest_v1/page/random/summary") as wiki:
            wiki_json = await wiki.json()

            await ctx.send(wiki_json['content_urls']['desktop']['page'])

    # table layout: guild id table name | keys (server config vars)
    @commands.command(aliases=["setreact","changereact"], description="switches reaction emoji used to post to bluesky")
    async def switchreact(self, ctx: commands.Context, user_emoji):
        #con = sqlite3.connect("files/configs.db")
        # cursor to interact w/ database
        #cur = con.cursor()

        table_name = f"guild_{ctx.guild.id}"

        query = '''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
        '''

        # checks if table exists
        guildTable = self.bot.cur.execute(query,(table_name,)).fetchall()

        # if table doesnt exist
        if not guildTable:
            print("creating table")
            query = f'''
            CREATE TABLE {table_name} (emoji TEXT)
            '''
            self.bot.cur.execute(query)
            # insert into table
            print("inserting into table")
            query = f'''
            INSERT INTO {table_name} (emoji)
            VALUES (?)
            '''
            self.bot.cur.execute(query,(user_emoji,))
            await ctx.send(f"{user_emoji}")
        # access existing table
        else:
            # updates values from table column
            print("clearing column data")
            delquery = f'''
            UPDATE {table_name}
            SET emoji = ?
            ''' # no WHERE because table will only have 1 emoji column, so clearing all doesnt matter
            self.bot.cur.execute(delquery,(user_emoji,))
            await ctx.send(f"{user_emoji}")
            
        self.bot.con.commit()

    @commands.command(aliases=["db"])
    @commands.is_owner()
    async def database(self, ctx: commands.Context):
        embed = discord.Embed(title="database")
        query = f'''
        SELECT name FROM sqlite_master WHERE type='table'
        '''
        dbStr = self.bot.cur.execute(query).fetchall()
        #await ctx.send(dbStr)

        dbFull = []
        # formatting like this auto unpacks the tuple
        for (table_name,) in dbStr:
            dbFull.append(table_name)
            dbFull.append(self.bot.cur.execute(f"SELECT * FROM {table_name}").fetchall())

        result = '\n'.join(str(x) for x in dbFull)
        embed.add_field(name="",value=result)
        print(result)
        #await ctx.send(embed=embed)

    @commands.command(description="checks the emoji used for guild votes and bluesky posts")
    async def check_guild_emoji(self, ctx: commands.Context):
        await ctx.send(await return_guild_emoji(ctx.guild.id, self.bot.cur, self.bot.defaultEmoji))

    @commands.command()
    @commands.is_owner()
    async def test_react(self, ctx: commands.Context):
        serverEmojis = ctx.message.guild.emojis
        guildBskyEmoji = await return_guild_emoji(ctx.guild.id, self.bot.cur, self.bot.defaultEmoji)
        randomEmoji = random.choice(serverEmojis)
        await ctx.send(f"{guildBskyEmoji}, {randomEmoji}")
        if str(randomEmoji) == str(guildBskyEmoji):
            await ctx.send("hawk")
        else:
            await ctx.send("tuah")


def setup(bot):
    bot.add_cog(Util(bot))