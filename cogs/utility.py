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
    @commands.command()
    async def switchreact(self, ctx: commands.Context, userEmoji):
        con = sqlite3.connect("files/configs.db")
        # cursor to interact w/ database
        cur = con.cursor()

        query = '''
        SELECT emoji FROM sqlite_master
        WHERE type='table' AND name=?

        '''
        guildID = ctx.guild.id

        # checks if table exists
        guildTable = cur.execute(query,(guildID)).fetchall()

        # if table doesnt exist
        if guildTable == []:
            cur.execute("CREATE TABLE ? (emoji)",(guildID))
        # access existing table
        else:
            pass

        con.commit()
        con.close()



def setup(bot):
    bot.add_cog(Util(bot))