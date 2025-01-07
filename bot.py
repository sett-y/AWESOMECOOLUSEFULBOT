import discord
from discord.ext import commands
import asyncio
import scripts.config
import os
import sys
import wavelink
from scripts.botimp import bot
import logging
import random

#TODO: custom prefixes (per server)

# important functions: ctx.channel | ctx.channel.history
# history contains messages
# to get message content from ctx.channel.history, use .content

# outputs error logs to discord.log file
logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger('discord')
#logger.setLevel(logging.DEBUG)
#handler = logging.FileHandler(filename='discord.log', encoding='uft-8', mode='w')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)

hawk = "hawk"

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            #cut off .py from filename
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception as e:
                print(f"problem loading extension: {e}")          
    print("extensions loaded")


@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    #await bot.change_presence(game=discord.Game(name="shut up Man", platform="yomama", type=1))


@bot.command(description="shuts down bot (owner only)")
@commands.is_owner()
async def shutdown(ctx):
    print("shutting down")
    await ctx.send("shutting down")
    try:
        await wavelink.Pool.close()
        await bot.close()
        print("shut down complete")
    except:
        print("error while shutting down")

    
@bot.command(description="restarts bot (owner only)")
@commands.is_owner()
async def restart(ctx):
    await wavelink.Pool.close()
    print("restarting")
    embed = discord.Embed(title=":white_check_mark: restarting :white_check_mark:")
    await ctx.send(embed=embed)
    #os.system("clear")
    os.execv(sys.executable, ['python'] + sys.argv)


@bot.command()
@commands.is_owner()
async def reload(ctx, arg):
    await bot.reload_extension(f"cogs.{arg}")
    await ctx.send(f"reloading extension: {arg}")


@bot.command(description="displays list of commands w/ descriptions")
async def commandlist(ctx):
    text = "```List of all bot commands:\n"
    for command in commands.commands:
        text += f">{command}"
        if command.description:
            text += f"\n[{command.description}]\n"
        else:
            text += '\n'
    text += "```"
    await ctx.send(text)


@bot.event
async def on_message(message: discord.Message):

    reactChance = random.random()

    # tuple of server emojis
    serverEmojis = message.guild.emojis
    if reactChance < 0.05:
        randomEmoji = random.choice(serverEmojis)
        await message.add_reaction(randomEmoji)

    if message.author == bot.user:
        return
    
    if message.content.startswith("bruh"):
        await message.channel.send("shut up")
    
    if hawk.lower() in message.content.lower():
        await message.channel.send("tuah")

    #apparently necessessary if i override the default on_message
    await bot.process_commands(message)

@bot.event
async def on_guild_emojis_update(guid, before, after):
    newEmoji = after[-1]
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(newEmoji)
                break


async def main():
    async with bot:
        await load_extensions()
        await bot.start(scripts.config.bot_token)


asyncio.run(main())

#TODO: add impact font to images