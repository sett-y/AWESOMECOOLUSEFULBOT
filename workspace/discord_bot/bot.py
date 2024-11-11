import discord
from discord.ext import commands
import asyncio
import scraper
import catFacts
import config
#import audioop
#import logging
#import subprocess

intents = discord.Intents.default()
intents.message_content = True
intents.presences = False

bot = commands.Bot(command_prefix = ">", description = "shut up", intents = intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    
@bot.command(description="shuts down bot (owner only)")
@commands.is_owner()
async def shutdown(ctx):
    print("shutting down")
    await ctx.send("shutting down")
    await bot.close()
    print("shut down complete")


@bot.command(description="displays info about dota match")
async def display_match(ctx):
    pass


@bot.command(name="catfact", description="displays a random cat fact")
async def catfact(ctx):
    #TODO: delete this after get_fact is done
    await ctx.send("loading cat fact...")
    catFact = await catFacts.get_fact()
    await ctx.send(catFact)


@bot.command(description="displays user join date")
async def joinDate(ctx):
    await ctx.send(discord.Member.created_at)


#TODO delete user's message right after sending
@bot.command(description="repeats user's message")
async def echo(ctx, *, arg):
    #TODO: needs perms
    #await ctx.message.delete()
    await ctx.send(arg)


@bot.command(description="displays list of commands w/ descriptions")
async def commandlist(ctx):
    text = "```List of all bot commands:\n"
    for command in bot.commands:
        text += f">{command}"
        text += f"     {command.description}\n"
    text += "```"
    await ctx.send(text)


@bot.event
async def on_message(message):
    #apparently necessessary if i override the default on_message
    await bot.process_commands(message)

    if message.author == bot.user:
        return
    
    if message.content.startswith("bruh"):
        await message.channel.send("shut up")



#change token before uploading to github
bot.run(config.bot_token)