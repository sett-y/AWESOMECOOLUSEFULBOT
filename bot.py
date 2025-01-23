import discord
from discord.ext import commands
import asyncio
import scripts.config
import os
import sys
import aiohttp
import wavelink
import logging
import random
#import tracemalloc

#TODO: custom prefixes (per server)
#TODO: block users
#TODO: image manipulation cmds
#lru_cache - saves N recent function calls
#islice - slices iterable, good for pagination
#single dispatch - overload function to take multiple types

# important functions: ctx.channel | ctx.channel.history
# history contains messages
# to get message content from ctx.channel.history, use .content

class AwesomeBot(commands.Bot):
    hawk: str
    session: aiohttp.ClientSession

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=[">","bc"], intents=intents)
        self.hawk = "hawk"
        self.session: aiohttp.ClientSession = None # aiohttp session
        self.logger = logging.basicConfig(level=logging.INFO) # logging

    async def load_extensions(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                #cut off .py from filename
                #try:
                self.load_extension(name=f"cogs.{filename[:-3]}")
                #except Exception as e:
                #    print(f"problem loading extension: {e}")
        print("extensions loaded")

    async def on_ready(self):
        print(f"logged in as {self.user}")

bot = AwesomeBot()

@bot.command(description="shuts down bot (owner only)")
@commands.is_owner()
async def shutdown(ctx: commands.Context):
    print("shutting down")
    await ctx.send("shutting down")
    await bot.session.close()
    await bot.close()
    print("shut down complete")

@bot.command(description="restarts bot (owner only)")
@commands.is_owner()
async def restart(ctx: commands.Context):
    print("restarting")
    #await bot.session.close()
    embed = discord.Embed(title=":white_check_mark: restarting :white_check_mark:")
    await ctx.send(embed=embed)
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
@commands.is_owner()
async def reload(ctx: commands.Context, arg):
    await bot.reload_extension(f"cogs.{arg}")
    await ctx.send(f"reloading extension: {arg}")

@bot.command(description="displays list of commands w/ descriptions")
async def commandlist(ctx: commands.Context):
    text = "```List of all bot commands:\n"
    for command in bot.commands:
        text += f">{command.name}"
        if command.description:
            text += f"\n[{command.description}]\n"
        else:
            text += '\n'
    text += "```"
    await ctx.send(text)

#@bot.check_once
#async def blacklist(ctx: commands.Context):
    # check database for user id

async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    
    reactChance = random.random()
    serverEmojis = message.guild.emojis
    if reactChance < 0.05:
        randomEmoji = random.choice(serverEmojis)
        await message.add_reaction(randomEmoji)
    elif reactChance < 0.005:
        randomEmoji = "🐲"
        await message.add_reaction(randomEmoji)
    
    if message.content.startswith("bruh"):
        await message.channel.send("shut up")

    if bot.hawk in message.content.lower():
        await message.channel.send("tuah")

    await bot.process_commands(message)

async def on_guild_emojis_update(guild: discord.Guild, before, after):
    newEmoji = after[-1]
    channel = guild.system_channel
    await channel.send(newEmoji)

async def on_member_join(member: discord.Member):
    await member.guild.system_channel.send(f"hi {member}")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if ctx.cog:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("command on cooldown")
    #await ctx.send(error)
    #if isinstance(error, commands.CommandOnCooldown):
    #    await ctx.send("command on cooldown")

async def main():
    async with bot:
        await bot.load_extensions()
        bot.session = aiohttp.ClientSession()
        if bot.session:
            print("aiohttp session started")
        else:
            print("aiohttp session failed to start")
        await bot.start(scripts.config.bot_token)

if __name__ == "__main__":
    asyncio.run(main())