from discord.ext import commands
import discord

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix = ">", description = "shut up", intents = intents)