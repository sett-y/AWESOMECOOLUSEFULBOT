from discord.ext import commands
import discord
import python_weather
import random
import scripts.reminder as reminder
from scripts.botimp import bot
from PIL import Image, ImageDraw, ImageFont


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="repeats user's message")
    async def echo(self, ctx, *, arg):
        #TODO: needs perms
        await ctx.message.delete()
        await ctx.send(arg)
        #await ctx.send(type(arg)) #arg = str

    @commands.command(description="displays weather stats using a wttr.in wrapper")
    async def weather(self, ctx, *, arg):
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


    @commands.command(description="troll face")
    async def troll(self, ctx):
        await ctx.message.delete()
        #messages can be assigned to variables to interact with them later
        #await ctx.send() returns a message object
        botmsg = await ctx.send("https://tenor.com/view/troll-troll-face-ragememe-rageface-trolling-gif-7857576152495722734")
        await botmsg.delete()

    @commands.command(description="sends a random cool website")
    async def website(self, ctx):
        websites = []
        with open("websites.txt", 'r') as file:
            for website in file:
                websites.append(website)
            w = websites[random.randint(0,len(websites)-1)].strip('\n')
            await ctx.send(w)

    @commands.command(name="reminder", description="send reminder msg, then enter numbers in subsequent msg:<hours> <minutes>")
    async def reminderTimer(self, ctx, *, arg):
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

        await ctx.send(f"reminding in {tmpHours} hour(s) and {tmpMinutes} minute(s)")
        message = await reminder.remind(reminderTime.content)
        print("sleep done")
        await ctx.send(f"{ctx.author.mention} {arg} {message[0]} {message[1]}")

    @commands.command()
    async def reversetext(self, ctx, *, msg):
        msg = msg[::-1]
        await ctx.send(msg)

    @commands.command()
    async def schoolalarm(self, ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/1163949682427433030/1324551380135837817/schoolalarm.gif?ex=67789019&is=67773e99&hm=f840c9dcb64160f64e4f0c48d3a2d51c23051ec04412c0bd29af6874249c50b2&")

    @commands.command(description="adds impact font to an image")
    async def impact(self, ctx, message: discord.Message):
        dscImg = message.attachments[0].url
        dscMsg = message.content
        await ctx.send(f"{dscMsg} {dscImg}")
        # prob need to pass as link or byte stream
        #image = Image.open(dscImg)
        #print(f"{image.format} {image.size}")

        #ImageFont

async def setup(bot):
    await bot.add_cog(Fun(bot))