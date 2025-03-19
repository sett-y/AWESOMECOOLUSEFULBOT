from discord.ext import commands
import discord
import traceback
from PIL import Image, ImageDraw, ImageFont
import io
import random
from bot import BotType
import scripts.helpers.db_helpers as db_helpers
from scripts.helpers.image_helpers import check_image
import textwrap

class ConfessionModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.TextInput(label="message"))
        self.add_item(discord.ui.TextInput(label="image attachment (optional)", required=False))

    async def on_submit(self, interaction: discord.Interaction):
        discolor = discord.Color
        colors = [discolor.red(), discolor.green(), discolor.blue()]
        colorChoice = random.choice(colors)
        embed = discord.Embed(title="Anonymous", color=colorChoice)
        
        childVal = self.children[0].value # type: ignore
        msg = childVal
        msg = f"\"{msg}\""

        embed.add_field(name="", value=msg)
        if childVal:
            imageAttachment = childVal
            
            embed.set_image(url=imageAttachment)
        else:
            imageAttachment = ""
            
        # print the user that submitted
        # normally i wouldnt want to track, but with image perms
        # its probably necessary
        print(f"{interaction.user.name}: {msg} {imageAttachment}")

        await interaction.response.defer()
        await interaction.channel.send(embed=embed, view=ButtonTest())

        originalMsg = await interaction.channel.fetch_message(interaction.message.id)
        await originalMsg.edit(view=None)

class ButtonTest(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Send Message", style=discord.ButtonStyle.primary)
    async def buttontest(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ConfessionModal(title="balls"))

class Database(commands.Cog):
    def __init__(self, bot: BotType):
        self.bot = bot
        self.lastMessage = None # 

    # helper function to check if table exists
    async def checkTable(self, tableName):
        query = f'''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='{tableName}'
        '''
        tableCheck = self.bot.cur.execute(query).fetchall()
        return tableCheck
    
    @commands.command()
    @commands.is_owner()
    async def post_changelog(self, ctx: commands.Context, *, log):
        tableCheck = self.checkTable("changelog")

        if not tableCheck:
            query = f'''
            CREATE TABLE changelog (log TEXT) 
            '''
            self.bot.cur.execute(query)

            # insert into columns with no values, update for existing vals
            query = f'''
            INSERT INTO changelog (log)
            VALUES (?)
            '''
            self.bot.cur.execute(query,(log,))
        else:
            query = f'''
            UPDATE changelog
            SET log = ?
            '''
            self.bot.cur.execute(query,(log,))

        self.bot.con.commit()
        await ctx.send("log added")

    @commands.command()
    async def changelog(self, ctx: commands.Context):
        query = f'''
        SELECT log FROM changelog
        '''
        try:
            log = self.bot.cur.execute(query).fetchall()
        except Exception as e:
            print(traceback.print_exc)
            print(e)

        await ctx.send(log[0][0])

    async def textWrap(self, message, maxLen):
        lineLen = 0
        numOfLines = 1
        wrappedMessage = ""
        for word in message.split(' '):
            while len(word) > maxLen:
                wrappedMessage += word[:maxLen] + '\n'
                word = word[maxLen:]
                lineLen = 0
                numOfLines += 1
            
            if lineLen + len(word) >= maxLen:
                wrappedMessage += f"\n{word} "
                lineLen = len(word) + 1
                numOfLines += 1
            else:
                wrappedMessage += f"{word} "
                lineLen = len(word) + 1
        return wrappedMessage.strip()

    async def loadTextImgFromUrl(self, url, text, username, background=None):
        buffer = io.BytesIO()
        font = ImageFont.truetype(font="files/fonts/0xProtoNerdFontMono-Regular.ttf", size=15)

        async with self.bot.session.get(url) as img:
            avatar_data = await img.read()
            if avatar_data:
                try:
                    avatarImage = Image.open(io.BytesIO(avatar_data))
                    avatarImage.thumbnail((150, 150))
                except Exception as e:
                    print(f"Failed to load avatar image: {e}")
                    return

                baseImage = Image.new(mode="RGB", size=(400, 400), color="black")  # Default black background

                if background:
                    print(f"Custom background URL: {background}")
                    try:
                        async with self.bot.session.get(background) as bg:
                            bg_data = await bg.read()
                            if bg_data:
                                try:  
                                    bg_image = Image.open(io.BytesIO(bg_data))
                                    print("Background image loaded successfully.")

                                    bg_width, bg_height = bg_image.size
                                    target_width, target_height = 400, 400

                                    scale = max(target_width / bg_width, target_height / bg_height)
                                    new_width = int(bg_width * scale)
                                    new_height = int(bg_height * scale)

                                    bg_image = bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

                                    left = (new_width - target_width) / 2
                                    top = (new_height - target_height) / 2
                                    right = (new_width + target_width) / 2
                                    bottom = (new_height + target_height) / 2

                                    bg_image = bg_image.crop((left, top, right, bottom))
                                    baseImage = bg_image
                                except Exception as e:
                                    print(f"Failed to process background image: {e}")
                                    # Fallback
                                    baseImage = Image.new(mode="RGB", size=(400, 400), color="black")
                    except Exception as e:
                        print(f"Failed to fetch background image: {e}")
                        # Fallback
                        baseImage = Image.new(mode="RGB", size=(400, 400), color="black")

                bioImage = ImageDraw.Draw(baseImage)
                base_width, base_height = baseImage.size

                wrapped_text = textwrap.fill(text, width=35)

                bioRec = [
                    (30, baseImage.height - 180), # Top-left
                    (baseImage.width - 30, baseImage.height - 20) # Bottom-right
                ]
                bioImage.rectangle(bioRec, outline="white", fill="black")

                bioX = bioRec[0][0] + 5
                bioY = bioRec[0][1] + 5
                try:
                    bioImage.multiline_text((bioX, bioY), text=wrapped_text, font=font, fill="white")
                except Exception as e:
                    print(f"Failed to draw text: {e}")

                # username
                #usernameX = (baseImage.width // 2) - (bioImage.textlength(username, font=font) / 2)
                #usernameY = (baseImage.height / 5.5) + (avatarImage.height)
                #bioImage.text((usernameX, usernameY), text=username, font=font)

                # avatar
                paste_width, paste_height = avatarImage.size
                x = (base_width - paste_width) / 2
                y = (base_height - paste_height) / 4.5
                baseImage.paste(avatarImage, (int(x), int(y)))

                baseImage.save(buffer, 'PNG')
                buffer.seek(0)
                return buffer
            else:
                print("URL is invalid")

    @commands.command(description="updates user's profile bio")
    async def bio(self, ctx: commands.Context, *, bio):
        if len(bio) > 2000:
            await ctx.send("bio too long")
            return

        profile_table = f"profile_{ctx.author.id}"
        tableCheck = await self.checkTable(profile_table)

        if not tableCheck:
            query = f'''
            CREATE TABLE {profile_table} (bio TEXT) 
            '''
            self.bot.cur.execute(query)

            query = f'''
            INSERT INTO {profile_table} (bio)
            VALUES (?)
            '''
            self.bot.cur.execute(query,(bio,))
            self.bot.con.commit()
        else:
            query = f'''
            UPDATE {profile_table}
            SET bio = ?
            '''
            self.bot.cur.execute(query,(bio,))
            self.bot.con.commit()
        await ctx.send("bio updated")

    @commands.command(description="displays user's profile")
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        if member and member.avatar:
            avatarUrl = member.avatar.url
            username = member.name
            profile_table = f"profile_{member.id}"
        else:
            if ctx.message and ctx.message.author.avatar:
                avatarUrl = ctx.message.author.avatar.url
                username = ctx.message.author.name
                profile_table = f"profile_{ctx.author.id}"
            else:
                print("no user found")

        profileQuery = f'''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='{profile_table}'
        '''
        profileTest = self.bot.cur.execute(profileQuery).fetchall()
        print(profileTest)
        defaultBG = "https://upload.wikimedia.org/wikipedia/en/7/73/Trollface.png"

        if not profileTest:
            query = f'''
            CREATE TABLE {profile_table} (bio TEXT)
            '''
            self.bot.cur.execute(query)

            query = f'''
            INSERT INTO {profile_table} (bio)
            VALUES ('gay ass stupid ass (>bio to change bio, >profilebg to change background)')
            '''
            self.bot.cur.execute(query)
            self.bot.con.commit()

            query = f'''
            SELECT bio FROM {profile_table}
            '''
            profile = self.bot.cur.execute(query).fetchall()

            # check if background has been set
            async with ctx.typing():
                bgExist = await db_helpers.check_column(profile_table, "profile_background", self.bot.cur)
                if bgExist[0][0] != 0:
                    profileBackground = await db_helpers.select_column(profile_table, "profile_background", self.bot.cur)
                else:
                    print("default bg")
                    profileBackground = defaultBG

                profileImage = await self.loadTextImgFromUrl(avatarUrl, profile[0][0], username, profileBackground)
                await ctx.send(file=discord.File(profileImage, "user_profile.png"))
        else:
            query = f'''
            SELECT bio FROM {profile_table}
            '''
            profile = self.bot.cur.execute(query).fetchall()

            async with ctx.typing():
                bgExist = await db_helpers.check_column(profile_table, "profile_background", self.bot.cur)
                if bgExist[0][0] != 0:
                    profileBackground = await db_helpers.select_column(profile_table, "profile_background", self.bot.cur)
                else:
                    print("default bg")
                    profileBackground = defaultBG

                profileImage = await self.loadTextImgFromUrl(avatarUrl, profile[0][0], username, profileBackground)
                await ctx.send(file=discord.File(profileImage, "user_profile.png"))

    @commands.command(aliases=["background"], description="sets background image for user's profile")
    async def profilebg(self, ctx: commands.Context, *, url=None):
        profile_table = f"profile_{ctx.author.id}"
        attachment_file = await check_image(ctx, url)
        
        if attachment_file is None:
            await ctx.send("include a valid url")
            return
        
        try:
            await db_helpers.update_column(profile_table, "profile_background", attachment_file, 
                                            self.bot.cur, self.bot.con)
        except Exception as e:
            print(e)

        await ctx.send("background added")

    # set channel for confession
    @commands.command(description="sets channel for confessions")
    async def confession(self, ctx: commands.Context):
        table_name = f"guild_{ctx.guild.id}"
        column_name = f"channel_{ctx.channel.id}"
        # remember to int cast when using value
        column_val = f"{ctx.channel.id}"
        print(f"setting channel {ctx.channel.name} as confessions channel")
        try:
            await db_helpers.update_column(table_name, column_name, column_val, self.bot.cur, self.bot.con)
        except Exception as e:
            print(e)
        else:
            await ctx.send(f"setting confession channel to {ctx.channel.name} ({ctx.channel.id})")   

    @commands.command(description="resets server confession channel")
    async def delconfession(self, ctx: commands.Context):
        table_name = f"guild_{ctx.guild.id}"
        column_name = f"channel_{ctx.channel.id}"
        await db_helpers.delete_column(table_name, column_name, self.bot.cur, self.bot.con)
        await ctx.send(f"resetting confession channel from {ctx.channel.name} ({ctx.channel.id})")
    
    @commands.command(description="checks current confession channel")
    async def checkconfession(self, ctx: commands.Context):
        table_name = f"guild_{ctx.guild.id}"
        column_name = f"channel_{ctx.channel.id}"
        conChannel = await db_helpers.select_column(table_name, column_name, self.bot.cur)
        await ctx.send(conChannel)

    @commands.command(aliases=["anon","anonmessage","anonymousmessage","anonymous"])
    async def message(self, ctx: commands.Context):
        view = ButtonTest()
        embed = discord.Embed(title="")
        embed.add_field(name="", value="Click to send a message:")
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

    # .t aww command
    


async def setup(bot):
    await bot.add_cog(Database(bot))