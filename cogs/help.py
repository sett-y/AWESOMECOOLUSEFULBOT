from discord.ext import commands
import discord
from bot import BotType

#TODO: replace help command with embed menu that has multiple pages

class HelpExtend(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page)
            await destination.send(embed=embed)

class Help(commands.Cog):
    def __init__(self, bot: BotType):
        self.bot = bot
        self.bot.help_command = HelpExtend()


async def setup(bot):
    await bot.add_cog(Help(bot))