from discord.ext import commands
import discord
import random
import scripts.reminder as reminder
import io
from typing import Optional, List
from bot import BotType
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageSequence
from scripts.helpers.image_helpers import check_image

#class FunFlags(commands.FlagConverter, prefix='-', delimiter=' '):
#    width: int = commands.flag(default=150)
#    height: int = commands.flag(default=150)

class ImageFlags(commands.FlagConverter):
    url: str = commands.flag(default=None, description="url to image")
    top: str = commands.flag(description="text for image")
    bottom: str = commands.flag(default=None, description="bottom text")
    #fontsize: int

class BallFlags(commands.FlagConverter):
    url: str = commands.flag(default=None, description="url of base image")
    x: int = commands.flag(default=None, description="x coord of balls")
    y: int = commands.flag(default=None, description="y coord of balls")
    size: int = commands.flag(default=None, description="size of image")

class RemoteEchoFlags(commands.FlagConverter):
    channel: int
    message: str

class Fun(commands.Cog):
    def __init__(self, bot: BotType):
        self.bot = bot
        self.avatarVote: List[int] = [] # store messages w/ active votes here
        self.userVoted: List[int] = []

    #@commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(description="repeats user's message", aliases=["print"])
    async def echo(self, ctx: commands.Context, *, message):
        botmessage = await ctx.send(message)
        await ctx.message.delete()

    #@commands.command(description="displays weather stats using a wttr.in wrapper")
    #async def weather(self, ctx: commands.Context, *, arg):
    #    tempEmoji = ""
    #    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
    #        weather = await client.get(arg)
    #        if weather.temperature > 90: tempEmoji+="🔥"
    #        elif weather.temperature > 68: tempEmoji+="🌞"
    #        elif weather.temperature > 55: tempEmoji+="⛅"
    #        else: tempEmoji+="🧊"
    #        await ctx.send(f"```City: {weather.location}\nCountry: {weather.country}\nTemperature: {tempEmoji}{weather.temperature}\
    #        \nHumidity: {weather.humidity}\nPrecipitation: {weather.precipitation}\nWind Speed: {weather.wind_speed}\n{weather.datetime}```")

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
            reminderTime = await self.wait_for("message", check = lambda msg: msg.author == ctx.author, timeout=60.0) # type: ignore
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

    @commands.command(aliases=["reversetxt"], description="reverses text")
    async def reversetext(self, ctx: commands.Context, *, msg):
        msg = msg[::-1]
        await ctx.send(msg)
        #TODO: reverse text from replies
        #TODO: if perms to delete msg, delete user's msg provided flag is used

    @commands.command(description="still better than school alarm")
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
    
        if (emo := ctx.guild):
            emoji_list = emo.emojis
        else:
            print("not in a guild")

        print(emoji_list[0].name)
        #await ctx.send(emoji_list[2])
        #:emoji_name:
        await ctx.send(new_fart)

    #TODO: fart config
    # ALTER TABLE guild_
    # ADD fart TEXT

    def votesNeeded(self, servMembers: int) -> int:
        if servMembers <= 30:
            return 3
        elif servMembers <= 100:
            return 4
        elif servMembers <= 200:
            return 5
        else:
            return 8

    @commands.command(aliases=["voteavatar","votepfp"])
    async def vote(self, ctx: commands.Context):
        guild_emoji = "👆"

        if ctx.message.attachments:
            self.avatarVote.append(ctx.message.id)
            #self.avatarVote[ctx.message.id] = ctx.message.attachments[0].url
            await ctx.message.add_reaction(guild_emoji)
            print("vote registered")
            print(ctx.message.attachments[0].url)
        elif "http" in ctx.message.content:
            self.avatarVote.append(ctx.message.id)
            #self.avatarVote[ctx.message.id] = ctx.message.content.strip()
            await ctx.message.add_reaction(guild_emoji)
            print("vote registered")
        else:
            await ctx.send("include an image with command")

    # 1 of certain event per cog
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        # delete message ################################################################
        deleteEmoji = "💣"
        if (rec := reaction.message.guild) and rec.member_count:
            servMembers = rec.member_count
            delvoteThreshold = self.votesNeeded(servMembers)
        else:
            print("not in a guild")
            return

        if reaction.emoji == "💣":
            for recemoji in reaction.message.reactions:
                if recemoji.emoji == "💣":
                    if recemoji.count == delvoteThreshold and reaction.emoji == deleteEmoji:
                        await reaction.message.delete()
                        await reaction.message.channel.send("💥")
                        return

        # change avatar #################################################################
        messageID = reaction.message.id
        content = reaction.message.content
        guild_emoji = "👆"
        voteThreshold = 4

        if (user.id in self.bot.specialUsers and 
            messageID in self.avatarVote and messageID not in self.userVoted 
            and reaction.emoji == self.bot.specialReact):
            print("special user reacted")
            reactNum = voteThreshold
            guild_emoji = self.bot.specialReact
        else:
            if reaction.emoji == guild_emoji:
                reactNum = reaction.count

        # checks if reacted message id has been recorded with vote command
        if messageID in self.avatarVote and reaction.emoji == guild_emoji and messageID not in self.userVoted:
            if reactNum >= voteThreshold:
                # once votes reach the threshold, this message is ignored
                self.userVoted.append(messageID)
                if reaction.message.attachments:
                    async with self.bot.session.get(reaction.message.attachments[0].url) as avatar:
                        if avatar.status == 200:
                            # avatar param wants bytes object, so aiohttp read() method is perfect
                            # can also use avatar.text, avatar.content.iter_chunked(chunk_size) to save to file
                            if self.bot.user:
                                await self.bot.user.edit(avatar=await avatar.read())
                                print("avatar changed")
                                await reaction.message.channel.send("yippee new avatar")
                        else:
                            await reaction.message.channel.send("could not download attachment")
                elif "http" in content:
                    start = len(">vote ")
                    content = content[start:]
                    async with self.bot.session.get(content.strip()) as avatar:
                        if avatar.status == 200:
                            if self.bot.user:
                                await self.bot.user.edit(avatar=await avatar.read())
                                print("avatar changed")
                                await reaction.message.channel.send("yippee new avatar")
                        else:
                            await reaction.message.channel.send("could not download attachment")
                else:
                    print("invalid message content")
                    await reaction.message.channel.send("only include an attachment or link in message")
        elif messageID in self.userVoted:
            print("message has reached threshold")

    @commands.command(aliases=["uselessfact"], description="get a random useless fact")
    async def fact(self, ctx: commands.Context):
        async with self.bot.session.get("https://uselessfacts.jsph.pl/api/v2/facts/random",
                                        headers={"Accept": "text/plain"}) as fact:
            data = await fact.text()
            await ctx.send(data)

    @commands.command(aliases=["coin"])
    async def coinflip(self, ctx: commands.Context):
        ra = random.random()
        if ra > 0.5:
            await ctx.send("heads")
        else:
            await ctx.send("tails")

    @commands.command(aliases=["flipimage"])
    async def flip(self, ctx: commands.Context, url: Optional[str]):
        async with ctx.channel.typing():
            attachment_file = await check_image(ctx, url)

            if attachment_file:
                async with self.bot.session.get(attachment_file) as attach:
                    image_data = await attach.read()
                    print("image data loaded")

                    if image_data:
                        im = Image.open(io.BytesIO(image_data)) # container for binary data, treated like file
                    else:
                        await ctx.send("invalid image")

                    buffer = io.BytesIO() # file object to save image into
                    transpose = im.transpose(Image.FLIP_TOP_BOTTOM) # type: ignore
                    transpose.save(buffer, 'PNG') # saves data into buffer
                    buffer.seek(0) # saving puts seek at last byte, so this resets it
                    await ctx.send(file=discord.File(buffer, "image.png"))
                    buffer.close()
                    #with io.BytesIO() as binary_image:
            else:
                print(f"attachment_file is None: {type(attachment_file)}")

    @commands.command(name="balls", description="usage: >balls x:<int> y:<int> url:<text> (arguments are optional)")
    async def balls(self, ctx: commands.Context, *, flags: BallFlags):
        ball = Image.open("files/images/balls.webp")
        buffer = io.BytesIO()

        if flags.url is not None:
            attachment_file = flags.url
        elif ctx.message.attachments:
            attachment_file = ctx.message.attachments[0].url
        else:
            # check for latest image in channel
            attachment_file = await check_image(ctx)

        async with ctx.channel.typing():
            if attachment_file:
                async with self.bot.session.get(attachment_file) as attach:
                    image_data = await attach.read()
                    if image_data:
                        im = Image.open(io.BytesIO(image_data))
                        if flags.x:
                            imgX = flags.x
                        else:
                            imgX = int(im.width / 2) - (ball.width // 2)
                        if flags.y:
                            imgY = flags.y
                        else:
                            imgY = int(im.height / 2) - (ball.height // 2)
                        im.paste(ball, (imgX, imgY)) # returns None, check docs from now on
                        im.save(buffer, 'PNG')
                        buffer.seek(0)
                        await ctx.send(file=discord.File(buffer, "balls.png"))
                        buffer.close()
            else:
                print(f"attachment_file is None: {type(attachment_file)}")

    @commands.command(aliases=["mono"], description="changes image to black and white")
    async def monochrome(self, ctx: commands.Context, url=None):
        buffer = io.BytesIO()
        attachment_file = await check_image(ctx, url)

        async with ctx.channel.typing():
            if attachment_file:
                async with self.bot.session.get(attachment_file) as attach:
                    image_data = await attach.read()
                    im = Image.open(io.BytesIO(image_data)).convert('RGBA')
                    grayscale = im.convert('L')
                    _, _, _, a = im.split()
                    mono = Image.merge('LA', (grayscale, a))
                    
                    mono.save(buffer, "PNG")
                    buffer.seek(0)
                    await ctx.send(file=discord.File(buffer, "monochrome.png"))
                    buffer.close()
            else:
                print(f"attachment_file is None: {attachment_file}")

    @commands.command()
    async def contrast(self, ctx: commands.Context, url=None):
        buffer = io.BytesIO()
        attachment_file = await check_image(ctx, url)

        async with ctx.channel.typing():
            if attachment_file:
                async with self.bot.session.get(attachment_file) as attach:
                    image_data = await attach.read()
                    im = Image.open(io.BytesIO(image_data))
                    
                    contrast_image = ImageEnhance.Contrast(im)
                    im = contrast_image.enhance(1.9)
                    #contrast_image2 = ImageEnhance.Sharpness()

                    bright = im.point(lambda i: i * 5)
                    bright.save(buffer, 'PNG')

                    buffer.seek(0)
                    await ctx.send(file=discord.File(buffer, "baked.png"))
                    buffer.close()
            else:
                print(f"attachment_file is None: {attachment_file}")

    @commands.command(description="usage: >impact top: <text> bottom: <text> url: <url> (only 1 argument is needed)")
    async def impact(self, ctx: commands.Context, *, flags: ImageFlags):
        buffer = io.BytesIO()
        if flags.url is not None:
            attachment_file = flags.url
        elif ctx.message.attachments:
            attachment_file = ctx.message.attachments[0].url
        else:
            # check for latest image in channel
            attachment_file = await check_image(ctx)

        async with ctx.channel.typing():
            if attachment_file:
                async with self.bot.session.get(attachment_file) as attach:
                    image_data = await attach.read()
                    base_image = Image.open(io.BytesIO(image_data))
                    
                    # scale text y offset based on image size
                    offsetY = base_image.height * 0.05
                    topTextPos = (base_image.width / 2, offsetY)
                    bottomTextPos = (base_image.width / 2, base_image.height - offsetY)

                    fontSize = 30
                    font = ImageFont.truetype("files/impact.ttf", size=fontSize)
                    # scale text based on image size
                    imgAvgSize = (base_image.size[0] + base_image.size[1]) / 2
                    while font.size < 0.1 * imgAvgSize:
                        fontSize += 1
                        font = ImageFont.truetype("files/impact.ttf", size=fontSize)
                    draw = ImageDraw.Draw(base_image)

                    # check for top text
                    if flags.top:
                        draw.text(topTextPos, text=flags.top, fill="white", font=font,
                                anchor="mt", stroke_width=4, stroke_fill="black")
                    # check for bottom text
                    if flags.bottom:
                        draw.text(bottomTextPos, text=flags.bottom, fill="white", font=font,
                                anchor="mb", stroke_width=4, stroke_fill="black")

                    base_image.save(buffer, 'PNG')
                    buffer.seek(0)
                    await ctx.send(file=discord.File(buffer, "impact.png"))
                    buffer.close()
            else:
                print(f"attachment_file is None: {attachment_file}")

    @commands.command(name="quote", description="generates a real quote by a user")
    async def quoteuser(self, ctx: commands.Context, member: Optional[discord.Member] = None,
                        *, message: Optional[str] = None):
        if message is None:
            await ctx.send("include a quote idiot")
            return
        buffer = io.BytesIO()

        async with ctx.channel.typing():
            if member and member.avatar:
                async with self.bot.session.get(member.avatar.url) as avatar:
                    if avatar.status != 200:
                        print("failed to fetch avatar")
                        return
                    member = member or ctx.author
                    image_data = await avatar.read()
                    avatar_image = Image.open(io.BytesIO(image_data))
                    avatar_image.thumbnail((150,150))

                    quote = Image.new(mode="RGB", size=(400,400))
                    draw = ImageDraw.Draw(quote)

                    font = ImageFont.truetype("files/fonts/0xProtoNerdFontMono-Regular.ttf", 25)

                    wrapped_message = ""
                    line_len = 0
                    max_len = 25
                    for word in message.split(' '):
                        while len(word) > max_len:
                            wrapped_message += word[:max_len] + '\n'
                            word = word[max_len:]
                            line_len = 0

                        if line_len + len(word) >= max_len:
                            wrapped_message += f"\n{word} "
                            line_len = len(word) + 1
                        else:
                            wrapped_message += f"{word} "
                            line_len += len(word) + 1
                    wrapped_message = wrapped_message[:-1]

                    user_quote = f"\"{wrapped_message}\"\n-{member.name}"
                    draw.text((0,0), user_quote, font=font) # text returns None

                    # paste avatar
                    quote.paste(avatar_image, (round(quote.width/3.5), quote.height//2))

                    quote.save(buffer, 'PNG')
                    buffer.seek(0)

                    await ctx.send(file=discord.File(buffer, "quote.png"))
                    buffer.close()
            else:
                print("no member included in argument")
                pass
                
    @commands.command()
    async def award(self, ctx: commands.Context, member: Optional[discord.Member], *, message: Optional[str]):
        buffer = io.BytesIO()
        font = ImageFont.truetype("files/impact.ttf", 20)

        if not message:
            await ctx.send("include a message")
            return
        if not member:
            print("no member included in arguments")
            return
        
        async with ctx.channel.typing():
            if member and member.avatar:
                async with self.bot.session.get(member.avatar.url) as avatar:
                    if avatar.status != 200:
                        print("failed to fetch avatar")
                        return
                    image_data = await avatar.read()
                    award_image = Image.open("files/images/award.png")
                    # add text to award
                    award_draw = ImageDraw.Draw(award_image)

                    wrapped_message = ""
                    line_len = 0
                    max_len = 13

                    for word in message.split(' '):
                        while len(word) > max_len:
                            wrapped_message += word[:max_len] + '\n'
                            word = word[max_len:]
                            line_len = 0
                        
                        if line_len + len(word) >= max_len:
                            wrapped_message += f"\n{word} "
                            line_len = len(word) + 1
                        else:
                            wrapped_message += f"{word} "
                            line_len += len(word) + 1
                    #wrapped_message = wrapped_message[:-1]

                    award_draw.text((award_image.width/5,award_image.height/5), 
                                    wrapped_message, fill=(0,0,0,255), font=font)

                    avatar_image = Image.open(io.BytesIO(image_data))
                    avatar_image.seek(0)
                    resize_avatar = avatar_image.resize((600,600))
                    resize_avatar.paste(award_image, (400, 400), award_image)
                    resize_avatar.save(buffer, 'PNG')
                    
                    buffer.seek(0)
                    await ctx.send(file=discord.File(buffer, filename="avatar_award.png"))
                    buffer.close()

    @commands.command(description="usage: >remote channel:<channel id> message:<message>")
    async def remote(self, ctx: commands.Context, *, flags: RemoteEchoFlags):
        chan = await self.bot.fetch_channel(flags.channel)
        await chan.send(flags.message)

    @commands.command(aliases=["reverse"], description="reverses a gif")
    async def reversegif(self, ctx: commands.Context, url=None):
        buffer = io.BytesIO()
        attachment_file = await check_image(ctx, url)

        async with ctx.channel.typing():
            if attachment_file:
                async with self.bot.session.get(attachment_file) as attach:
                    image_data = await attach.read()

                    try:
                        animated_image = Image.open(io.BytesIO(image_data))
                    except IOError as e:
                        await ctx.send("image is not a gif (if you sent a tenor link that wont work, since its not a direct embed)")
                        print(f"not a gif: {e}")
                        return
                    except Exception as e:
                        print(e)
                        return
                    
                    frames = [frame.copy() for frame in ImageSequence.Iterator(animated_image)]
                    frames.reverse()

                    frames[0].save(
                        buffer,
                        format="GIF",
                        save_all=True,
                        append_images=frames[1:],
                        loop=0,
                        duration=animated_image.info['duration']
                    )
                    buffer.seek(0)
                await ctx.send(file=discord.File(buffer, filename="reversed.gif"))
            else:
                print(f"attachment_file is None: {attachment_file}")
           

# TODO: let users invoke commands on messages by replying to them

    """
        idea: userphone-like command that searches for connection to another server,
        and sends messages back and forth between servers
        
        pseudo code, ignore this

        for id in id_list:
            
    """

async def setup(bot):
    await bot.add_cog(Fun(bot))