import discord
from discord.ext import commands
import asyncio
import scraper
import catFacts
import config
import python_weather
import ytmp3
import os
import sys
import random
import reminder
import gemini
#import easy_pil
#import audioop
#import logging
#import subprocess
intents = discord.Intents.default()
intents.message_content = True
intents.presences = False
hawk = "hawk"

bot = commands.Bot(command_prefix = ">", description = "shut up", intents = intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")


@bot.command(description="shuts down bot (owner only)")
@commands.is_owner()
async def shutdown(ctx):
    print("shutting down")
    await ctx.send("shutting down")
    try:
        await bot.close()
        print("shut down complete")
    except:
        print("error while shutting down")

    
@bot.command(description="restarts bot (owner only)")
@commands.is_owner()
async def restart(ctx):
    print("restarting")
    embed = discord.Embed(title=":white_check_mark: restarting :white_check_mark:")
    await ctx.send(embed=embed)
    #os.system("clear")
    os.execv(sys.executable, ['python'] + sys.argv)


@bot.command(description="displays info about dota match")
async def display_match(ctx, url):
    await ctx.send("fetching match...")
    html = await scraper.call_scraper("get_match_info", url)
    await ctx.send(html)
    #for h in html:
        #await ctx.send(h)


@bot.command(description="displays info about user dotabuff profile")
async def display_profile(ctx, url):
    await ctx.send("fetching profile...")
    html = await scraper.call_scraper("parse_profile", url)
    #for h in html:
        #await ctx.send(h)


@bot.command(name="catfact", description="displays a random cat fact")
async def catfact(ctx):
    #TODO: delete this after get_fact is done
    await ctx.send("loading cat fact...")
    try:
        catFact = await catFacts.get_fact()
        await ctx.send(catFact)
    except:
        print("error while scraping page")


@bot.command()
async def weather(ctx, *, arg):
    tempEmoji = ""
    humEmoji = ""
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(arg)
        if weather.temperature > 90: tempEmoji+="🔥"
        elif weather.temperature > 68: tempEmoji+="🌞"
        elif weather.temperature > 55: tempEmoji+="⛅"
        else: tempEmoji+="🧊"
        await ctx.send(f"```City: {weather.location}\nCountry: {weather.country}\nTemperature: {tempEmoji}{weather.temperature}\
        \nHumidity: {weather.humidity}\nPrecipitation: {weather.precipitation}\nWind Speed: {weather.wind_speed}\n{weather.datetime}```")


@bot.command(name="mp3", description="takes a youtube url and sends the audio as an mp3")
async def mp3(ctx, url):
    try:
        file_path = await asyncio.to_thread(ytmp3.yt2mp3, url)
        print(f"file path: {file_path}")

    except Exception as e:
        print(f"error downloading: {e}")
        await ctx.send(f"error downloading: {e}")
        
    if file_path:
        await ctx.send("download successful")

        if await ctx.send(file=discord.File(file_path)):
            print("valid upload size")
            #await ctx.send("valid upload size")
        else:
            print("file too large")
            ctx.send("file too large")
    tmp = ytmp3.yttitle
    os.remove(os.getcwd() + "\\" + tmp + ".mp3")


@bot.command(name="mp4", description="takes a youtube url and sends video as mp4")
async def mp4(ctx, url):
    try:
        file_path = await asyncio.to_thread(ytmp3.yt2mp4, url)
        print(f"file path: {file_path}")

    except Exception as e:
            print(f"error downloading: {e}")
            await ctx.send(f"error downloading: {e}")
    
    if file_path:
        await ctx.send("download successful")
        
        if await ctx.send(file=discord.File(file_path)):
            print("valid upload size")
            #await ctx.send("valid upload size")
        else:
            print("file too large")
            await ctx.send("file too large")
    tmp = ytmp3.yt4title
    os.remove(os.getcwd() + "\\" + tmp + ".mp4")


@bot.command()
async def delivery_notif(ctx, url):
    pass


@bot.command(description="sends link to user pfp, can specify user with a ping")
async def pfp(ctx, member: discord.Member = None):
    member = member or ctx.author
    pfp = member.avatar.url
    await ctx.send(pfp)


@bot.command()
async def servpic(ctx):
    pass


@bot.command(description="displays user join date")
async def joinDate(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"Account Created: {member.created_at}\n\
Server Joined: {member.joined_at}")
    #await ctx.send(member._client_status)


@bot.command(description="repeats user's message")
async def echo(ctx, *, arg):
    #TODO: needs perms
    await ctx.message.delete()
    await ctx.send(arg)
    #await ctx.send(type(arg)) #arg = str


@bot.command(description="troll face")
async def troll(ctx):
    await ctx.message.delete()
    #messages can be assigned to variables to interact with them later
    #await ctx.send() returns a message object
    botmsg = await ctx.send("https://tenor.com/view/troll-troll-face-ragememe-rageface-trolling-gif-7857576152495722734")
    await botmsg.delete()
    

@bot.command(description="sends a random cool website")
async def website(ctx):
    websites = []
    with open("websites.txt", 'r') as file:
        for website in file:
            websites.append(website)
        w = websites[random.randint(0,len(websites)-1)].strip('\n')
        await ctx.send(w)


@bot.command(name="fortune", description="prompt google gemini to generate a fortune")
async def fortunecookie(ctx):
    await ctx.send("reading fortune...")
    fortune = await gemini.fortune()
    print("generated")
    await ctx.send(f"🥠 {fortune} 🥠")


@bot.command(name="ascii", description="generate ascii art based on user prompt")
async def asciiGen(ctx, *, arg):
    await ctx.send("generating ascii...")
    ascii = await gemini.asciiArt(arg)
    print("generated")
    await ctx.send(f"```{ascii}```")


@bot.command(name="prompt", description="generate a response based on prompt given")
async def prompt(ctx, *, arg):
    await ctx.send("generating response...")
    response = await gemini.genericPrompt(arg)
    print("response generated")
    await ctx.send(response)


@bot.command(name="reminder", description="send reminder msg, then enter numbers in subsequent msg:<hours> <minutes>")
async def reminderTimer(ctx, *, arg):
    tmpMinutes = 0
    tmpHours = 0

    #user input for time
    try:
        await ctx.send("enter time")
        reminderTime = await bot.wait_for("message", check = lambda msg: msg.author == ctx.author, timeout=60.0)
    except Exception as e:
        print(e)
        await ctx.send(e)

    #remember to use .content when working with message objects
    remTime = reminderTime.content
    remTime = remTime.split(' ')

    if len(remTime) == 1:
        tmpHours = remTime[0]
    else:
        tmpHours = remTime[0]
        tmpMinutes = remTime[1]

    await ctx.send(f"reninding in {tmpHours} hour(s) and {tmpMinutes} minute(s)")
    message = await reminder.remind(reminderTime.content)
    print("sleep done")
    await ctx.send(f"{ctx.author.mention} {arg} {message[0]} {message[1]}")
    

@bot.command(description="displays list of commands w/ descriptions")
async def commandlist(ctx):
    text = "```List of all bot commands:\n"
    for command in bot.commands:
        text += f">{command}"
        if command.description:
            text += f"\n[{command.description}]\n"
        else:
            text += '\n'
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
    
    if hawk.lower() in message.content.lower():
        await message.channel.send("tuah")


@bot.event
async def on_guild_emojis_update(guid, before, after):
    newEmoji = after[-1]
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(newEmoji)
                break


bot.run(config.bot_token)