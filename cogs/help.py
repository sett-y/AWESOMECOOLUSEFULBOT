from discord.ext import commands
import discord

#TODO: replace help command with embed menu that has multiple pages

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Help(bot))