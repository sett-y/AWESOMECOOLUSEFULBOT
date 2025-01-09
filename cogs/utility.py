from discord.ext import commands
import discord
from scripts.googlescrape import get_search

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

    @commands.command(aliases=["pfp","avatar"], description="sends link to user pfp, can specify user with a ping")
    async def get_avatar(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        pfp = member.avatar.url
        await ctx.send(pfp)

    @commands.command()
    async def delivery_notif(self, ctx: commands.Context, url):
        pass

    @commands.command(description='google search! ! ')
    async def google(self, ctx: commands.Context, *, search_term):
        embed = discord.Embed(title="gooel")
        data = await get_search(search_term)
        for i in range(len(data)):
            title = value=data[i]['title']
            url = value=data[i]['url']
            embed.add_field(name="Result:", value=f'[{title}]({url})')
            #embed.add_field(name="url", value=data[i]['url'])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Util(bot))