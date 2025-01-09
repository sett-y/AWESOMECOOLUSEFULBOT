from discord.ext import commands
import discord
import python_weather
import random
import scripts.reminder as reminder
from scripts.botimp import bot
from PIL import Image, ImageDraw, ImageFont

#TODO: bot randomly reacts to messages with random emoji

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="repeats user's message", aliases=["print"])
    async def echo(self, ctx: commands.Context, *, arg):
        #TODO: needs perms
        await ctx.message.delete()
        await ctx.send(arg)

    @commands.command(description="displays weather stats using a wttr.in wrapper")
    async def weather(self, ctx: commands.Context, *, arg):
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
    async def troll(self, ctx: commands.Context):
        await ctx.message.delete()
        #messages can be assigned to variables to interact with them later
        #await ctx.send() returns a message object
        botmsg = await ctx.send("https://tenor.com/view/troll-troll-face-ragememe-rageface-trolling-gif-7857576152495722734")
        await botmsg.delete()

    @commands.command(description="sends a random cool website", aliases=["site"])
    async def website(self, ctx: commands.Context):
        websites = []
        with open("websites.txt", 'r') as file:
            for website in file:
                websites.append(website)
            w = websites[random.randint(0,len(websites)-1)].strip('\n')
            await ctx.send(w)

    @commands.command(aliases=["remind"], description="send reminder msg, then enter numbers in subsequent msg:<hours> <minutes>")
    async def reminder(self, ctx: commands.Context, *, arg):
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

    @commands.command(aliases=["reverse","reversetext","reversetxt"])
    async def reverseText(self, ctx: commands.Context, *, msg):
        msg = msg[::-1]
        await ctx.send(msg)
        #TODO: reverse text from replies
        #TODO: if perms to delete msg, delete user's msg provided flag is used

    @commands.command()
    async def schoolalarm(self, ctx: commands.Context):
        await ctx.send("https://cdn.discordapp.com/attachments/1163949682427433030/1324551380135837817/schoolalarm.gif?ex=67789019&is=67773e99&hm=f840c9dcb64160f64e4f0c48d3a2d51c23051ec04412c0bd29af6874249c50b2&")

    @commands.command(description=",little brap ;)")
    async def fart(self, ctx: commands.Context):
        fart_length = random.randint(10, 30)
        fart_characters = ('p','p','p','r','r','e','r','a','f','f',' ', '\U0001F4A9')
        fart_string = []

        for _ in range(fart_length):
            fart_char = random.choice(fart_characters)
            fart_string.append(fart_char)

        new_fart = ''.join(str(x) for x in fart_string)
    
        emoji_list = ctx.guild.emojis
        print(emoji_list[0].name)
        #await ctx.send(emoji_list[2])
        #:emoji_name:
        await ctx.send(new_fart)

    @commands.command(description="adds impact font to an image")
    async def impact(self, ctx: commands.Context, message: discord.Message):
        dscImg = message.attachments[0].url
        dscMsg = message.content
        await ctx.send(f"{dscMsg} {dscImg}")
        # prob need to pass as link or byte stream
        #image = Image.open(dscImg)
        #print(f"{image.format} {image.size}")

        #ImageFont

def setup(bot):
    bot.add_cog(Fun(bot))