from discord.ext import commands
import discord

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

    @commands.command()
    async def google(self, ctx: commands.Context):
        pass


def setup(bot):
    bot.add_cog(Util(bot))