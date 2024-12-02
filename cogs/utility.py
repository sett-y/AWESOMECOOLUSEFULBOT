from discord.ext import commands
import discord

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="fetches server picture")
    async def servpic(self, ctx):
        pass

    @commands.command(description="displays user join date")
    async def joinDate(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(f"Account Created: {member.created_at}\n\
        Server Joined: {member.joined_at}")
        #await ctx.send(member._client_status)

    @commands.command(description="sends link to user pfp, can specify user with a ping")
    async def pfp(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        pfp = member.avatar.url
        await ctx.send(pfp)

    @commands.command()
    async def delivery_notif(self, ctx, url):
        pass

    @commands.command()
    async def binary(self, ctx, num: int):
        binary = []
        for i in range(31, -1, -1):
            k = num >> i
            if (k&i):
                binary.append(1)
            else:
                binary.append(0)
        print(binary)
        await ctx.send(str(binary))


async def setup(bot):
    await bot.add_cog(Util(bot))