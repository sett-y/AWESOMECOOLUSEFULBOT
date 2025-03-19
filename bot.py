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
from typing import Optional
from scripts.helpers.db_helpers import return_guild_emoji
#from transformers import AutoTokenizer, AutoModelForCausalLM

# this allows type hints to work across different files
class BotType(commands.Bot):
    session: aiohttp.ClientSession
    con: sqlite3.Connection
    cur: sqlite3.Cursor
    logger: None

    # child specific values first, then *args and **kwargs to pass values on to parent function
    def __init__(self, *args, **kwargs):
        # this unpacks the tuple and dictionary into the parent function
        super().__init__(*args, **kwargs)
        self.con = sqlite3.connect("files/configs.db")
        self.cur = self.con.cursor()
        self.logger = logging.basicConfig(level=logging.INFO)
        self.hawk = "hawk"
        self.defaultEmoji = "🚎"
        self.specialUsers = frozenset({774068548322328606,203249661501243392,780307179768250388,111616497641660416})
        self.specialReact = "🦶"
        #bot.modelName = "EleutherAI/gpt-neo-1.3B"
        #bot.tokenizer = None
        #bot.model = None

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = BotType(command_prefix=[">", "bc"], intents=intents, help_command=commands.MinimalHelpCommand())

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
    reactChance = random.random()
    # check if message is in guild and not dm
    if message.guild:
        serverEmojis = message.guild.emojis
        if reactChance < 0.04 and reactChance > 0.0004 and not message.author.bot:
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
            if isinstance(logChannel, (discord.TextChannel, discord.Thread)):
                await logChannel.send(embed=embed)

        # zz troll orbit
        # zz id: 155120411070300160
        if message.reference:
            if isinstance(message.reference.message_id, int):
                referencedMessage = await message.channel.fetch_message(message.reference.message_id)
                # kevin hart
                if referencedMessage.author.id == 275071431304282122:
                    await message.add_reaction("🛰")
        
        # test this
        if any(user.id == 275071431304282122 for user in message.mentions):
            # emma id 275071431304282122
            await message.add_reaction("🛰")

        if message.mentions:
            if 275071431304282122 in message.mentions:
                # mypy wants a check to see if guild is None, since dm channels would return None
                if message.guild is not None:
                    userObject = await message.guild.fetch_member(275071431304282122)
                    if userObject in message.mentions:
                        await message.add_reaction("🛰")

    if message.content.startswith("bruh"):
        await message.channel.send("shut up")

    if bot.hawk in message.content.lower():
        await message.channel.send("tuah")

    if "brian look out" in message.content.lower():
        await message.channel.send("https://tenor.com/view/brian-family-guy-family-guy-sad-moment-brian-death-death-gif-19315370")

    if "only a spoonful" in message.content.lower():
        await message.channel.send("https://tenor.com/view/spoon-big-spoon-funny-mad-evil-stare-gif-17762991")

    if "did you bring a light" in message.content.lower():
        await message.channel.send("https://tenor.com/view/hotel-mario-mario-cdi-no-refusal-gif-3231775313720996150")

    if "cheers big ears" in message.content.lower():
        await message.channel.send("thats how it goes big nose")

    await bot.process_commands(message)

@bot.command(description="shuts down bot (owner only)")
@commands.is_owner()
async def shutdown(ctx: commands.Context):
    print("shutting down")
    await ctx.send("shutting down")
    if bot.con and bot.session:
        bot.con.close()
        await bot.session.close()
        await asyncio.sleep(0)
        await bot.close()
        print("shut down complete")

@bot.command(aliases=["Restart"],description="restarts bot (owner only)")
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

@bot.command()
async def shut_down(ctx: commands.Context):
    await ctx.send("shutting down")

@bot.event
async def on_guild_emojis_update(guild: discord.Guild, before, after):
    if guild:
        newEmoji = after[-1]
        channel = guild.system_channel
        if channel:
            await channel.send(newEmoji)

@bot.event
async def on_member_join(member: discord.Member):
    if isinstance(member.guild, discord.Guild) and isinstance(member.guild.system_channel, discord.TextChannel):
        await member.guild.system_channel.send(f"hi {member}")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if ctx.cog:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("command on cooldown")

@bot.before_invoke
async def check_if_blocked(ctx: commands.Context):
    blockList = [1246157498969493599] # j
    if ctx.author.id in blockList:
        print(f"user {ctx.author.name} is blocked")
        raise commands.CommandInvokeError(Exception(f"user {ctx.author.name} is blocked"))

async def main():
    async with bot:
        await load_extensions()
        bot.session = aiohttp.ClientSession()

        #bot.tokenizer = AutoTokenizer.from_pretrained(bot.modelName)
        #bot.model = AutoModelForCausalLM(bot.modelName)

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