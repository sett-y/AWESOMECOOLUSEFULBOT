from discord.ext import commands
import discord
from scripts.googlescrape import get_search
import sqlite3
import os

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="fetches server picture")
    async def servpic(self, ctx: commands.Context):
        ctx.send(ctx.guild.icon)

    @commands.command(description="displays user join date")
    async def joinDate(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(f"Account Created: {member.created_at}\n\
        Server Joined: {member.joined_at}")
        #await ctx.send(member._client_status)

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
        for c in self.bot.commands:
            commandList.append(f"{c.name} - {c.aliases}\n")
        cmdList = ''.join(str(c) for c in commandList)
        await ctx.send(cmdList)

    @commands.command(aliases=["wikipedia","wikisearch"], description="searches wikipedia")
    async def wiki(self, ctx: commands.Context, *, search):
        await ctx.send(f"https://en.wikipedia.org/wiki/{search}")

    # table layout: guild id table name | keys (server config vars)
    @commands.command(aliases=["setreact","changereact"])
    async def switchreact(self, ctx: commands.Context, userEmoji):
        con = sqlite3.connect("files/configs.db")
        # cursor to interact w/ database
        cur = con.cursor()

        table_name = f"guild_{ctx.guild.id}"

        query = '''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
        '''

        # checks if table exists
        guildTable = cur.execute(query,(table_name,)).fetchall()

        # if table doesnt exist
        if not guildTable:
            print("creating table")
            query = f'''
            CREATE TABLE {table_name} (emoji TEXT)
            '''
            cur.execute(query)
            # insert into table
            print("inserting into table")
            query = f'''
            INSERT INTO {table_name} (emoji)
            VALUES (?)
            '''
            cur.execute(query,(userEmoji,))
            await ctx.send(f"{userEmoji}")
        # access existing table
        else:
            # delete values from table column
            print("clearing column data")
            delquery = f'''
            UPDATE {table_name}
            SET emoji = ?
            '''
            cur.execute(delquery,(userEmoji,))
            await ctx.send(f"{userEmoji}")
            
        con.commit()
        con.close()

    @commands.command(aliases=["db"])
    @commands.is_owner()
    async def database(self, ctx: commands.Context):
        #table_name = f"guild_{ctx.guild.id}"
        con = sqlite3.connect("files/configs.db")
        cur = con.cursor()
        query = f'''
        SELECT name FROM sqlite_master WHERE type='table'
        '''
        dbStr = cur.execute(query).fetchall()
        #await ctx.send(dbStr)

        dbFull = []
        # formatting like this auto unpacks the tuple
        for (table_name,) in dbStr:
            dbFull.append(table_name)
            dbFull.append(cur.execute(f"SELECT * FROM {table_name}").fetchall())

        result = '\n'.join(str(x) for x in dbFull)
        await ctx.send(result)


def setup(bot):
    bot.add_cog(Util(bot))