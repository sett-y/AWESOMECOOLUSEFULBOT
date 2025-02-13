import discord
from discord.ext import commands
import asyncio
import scripts.config
import os
import sys
import aiohttp
import logging
import random
import sqlite3
from scripts.helpers.db_helpers import return_guild_emoji

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=[">", "bc"], intents=intents, help_command=commands.MinimalHelpCommand())
bot.logger = logging.basicConfig(level=logging.INFO)

# Global variables
bot.hawk = "hawk"
bot.session = None
bot.con = None
bot.cur = None
bot.defaultEmoji = "🚎"

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(name=f"cogs.{filename[:-3]}")
    print("extensions loaded")

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    # dont include bot's messages?

    reactChance = random.random()
    serverEmojis = message.guild.emojis
    if reactChance < 0.04 and reactChance > 0.0004:
        # check for guild emoji
        guildBskyEmoji = await return_guild_emoji(message.guild.id, bot.cur, bot.defaultEmoji)
        randomEmoji = random.choice(serverEmojis)
        if str(guildBskyEmoji) == str(randomEmoji):
            return
        try:
            await message.add_reaction(randomEmoji)
        except discord.Forbidden as e:
            print(e)
            print(f"bot is blocked by {message.author.name}")
        except Exception as e:
            print(e)
    elif reactChance <= 0.0004:
        dragonEmoji = "🐲"
        try:
            await message.add_reaction(dragonEmoji)
        except discord.Forbidden as e:
            print(e)
            print(f"bot is blocked by {message.author.name}")
        except Exception as e:
            print(e)
        await message.channel.send("DRAGON ALERT!!!!!", file=discord.File("files/images/dragonaward.png","dragon_award.png"))
    
    # user tracking
    if message.author.id == 155120411070300160: # zz
        if message.content:
            #TODO: check for attachments and send those? maybe not worth the effort
            logChannel = bot.get_channel(1336213895953518614)
            embed = discord.Embed(title="")
            embed.add_field(name="", value=message.jump_url, inline=False)
            embed.add_field(name="", value=message.content)
            await logChannel.send(embed=embed)

    if message.content.startswith("bruh"):
        await message.channel.send("shut up")

    if bot.hawk in message.content.lower():
        await message.channel.send("tuah")

    if "brian look out" in message.content.lower():
        await message.channel.send("https://tenor.com/view/brian-family-guy-family-guy-sad-moment-brian-death-death-gif-19315370")

    if "only a spoonfull" in message.content.lower():
        await message.channel.send("https://tenor.com/view/spoon-big-spoon-funny-mad-evil-stare-gif-17762991")

    await bot.process_commands(message)

@bot.command(description="shuts down bot (owner only)")
@commands.is_owner()
async def shutdown(ctx: commands.Context):
    print("shutting down")
    await ctx.send("shutting down")
    bot.con.close()
    await bot.session.close()
    await asyncio.sleep(0)
    await bot.close()
    print("shut down complete")

@bot.command(description="restarts bot (owner only)")
@commands.is_owner()
async def restart(ctx: commands.Context):
    print("restarting")
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

@bot.event
async def on_guild_emojis_update(guild: discord.Guild, before, after):
    newEmoji = after[-1]
    channel = guild.system_channel
    await channel.send(newEmoji)

@bot.event
async def on_member_join(member: discord.Member):
    await member.guild.system_channel.send(f"hi {member}")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if ctx.cog:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("command on cooldown")

async def main():
    async with bot:
        await load_extensions()
        bot.con = sqlite3.connect("files/configs.db")
        bot.cur = bot.con.cursor()
        bot.session = aiohttp.ClientSession()

        if bot.session:
            print("aiohttp session started")
        else:
            print("aiohttp session failed to start")
        if bot.con and bot.cur:
            print("sqlite connection started")
        else:
            print("sqlite failed to start")
        await bot.start(scripts.config.bot_token)

if __name__ == "__main__":
    asyncio.run(main())