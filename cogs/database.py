from discord.ext import commands
import discord
import traceback
from PIL import Image, ImageDraw, ImageFont
import io
import random
import scripts.helpers.db_helpers as db_helpers

class ConfessionModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.TextInput(label="text"))

    async def on_submit(self, interaction: discord.Interaction):
        discolor = discord.Color
        colors = [discolor.red(), discolor.green(), discolor.blue()]
        colorChoice = random.choice(colors)
        embed = discord.Embed(title="Anonymous", color=colorChoice)
        
        msg = self.children[0].value
        msg = f"\"{msg}\""
        embed.add_field(name="", value=msg)
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
    def __init__(self, bot):
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
        #print(wrappedMessage)
        return wrappedMessage.strip()

    async def loadTextImgFromUrl(self, url, text, username):
        buffer = io.BytesIO()
        font = ImageFont.truetype(font="files/fonts/0xProtoNerdFontMono-Regular.ttf", size=15)

        async with self.bot.session.get(url) as img:
            avatar_data = await img.read()
            if avatar_data:
                avatarImage = Image.open(io.BytesIO(avatar_data))
                avatarImage.thumbnail((150,150))
                baseImage = Image.new(mode="RGB", size=(400,400))
                bioImage = ImageDraw.Draw(baseImage) # base image with text
                base_width, base_height = baseImage.size

                wrapped_text = await self.textWrap(message=text, maxLen=20)
                
                # username text
                usernameX = (baseImage.width // 2) - (bioImage.textlength(username, font=font) / 2)
                usernameY = (baseImage.height / 5.5) + (avatarImage.height)
                bioImage.text((usernameX,usernameY), text=username, font=font)

                # bio text
                bbox = bioImage.multiline_textbbox((0,0), wrapped_text, font=font)
                #bioWidth = bbox[2] - bbox[0]
                #bioHeight = bbox[3] - bbox[1]

                bioX = (baseImage.width // 3) - 10
                bioY = usernameY + 40

                # TODO: bio text box fixed size
                bioRec = [
                    (30, baseImage.height - 180),
                    (baseImage.width - 30, baseImage.height - 20)
                ]
                #bioRec = [
                #    (bioX - 4, bioY - 2),
                #    (bioX + bioWidth + 4, (bioY + bioHeight + 10))
                #]
                
                bioImage.rectangle(bioRec, outline="white", fill="black")
                bioImage.multiline_text((bioX, bioY), text=wrapped_text, font=font, fill="white")

                # avatar placement
                paste_width, paste_height = avatarImage.size
                x = (base_width - paste_width) // 2
                y = (base_height - paste_height) / 4.5
                baseImage.paste(avatarImage, (int(x),int(y)))

                baseImage.save(buffer, 'PNG')
                buffer.seek(0)
                return buffer
            else:
                print("url is invalid")

    @commands.command(description="updates user's profile bio")
    async def bio(self, ctx: commands.Context, *, bio):
        if len(bio) > 3000:
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

    # TODO: user can upload a background image for their profile
    @commands.command(description="displays user's profile")
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        if member is None:
            avatarUrl = ctx.message.author.avatar.url
            username = ctx.message.author.name
            profile_table = f"profile_{ctx.author.id}"
        else:
            avatarUrl = member.avatar.url
            username = member.name
            profile_table = f"profile_{member.id}"

        profileQuery = f'''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='{profile_table}'
        '''
        profileTest = self.bot.cur.execute(profileQuery).fetchall()

        if not profileTest:
            query = f'''
            CREATE TABLE {profile_table} (bio TEXT)
            '''
            self.bot.cur.execute(query)

            query = f'''
            INSERT INTO {profile_table} (bio)
            VALUES ('gay ass stupid ass')
            '''
            self.bot.cur.execute(query)
            self.bot.con.commit()

            query = f'''
            SELECT bio FROM {profile_table}
            '''
            profile = self.bot.cur.execute(query).fetchall()
            profileImage = await self.loadTextImgFromUrl(avatarUrl, profile[0][0], username)
            await ctx.send(file=discord.File(profileImage, "user_profile.png"))
        else:
            query = f'''
            SELECT bio FROM {profile_table}
            '''
            profile = self.bot.cur.execute(query).fetchall()
            profileImage = await self.loadTextImgFromUrl(avatarUrl, profile[0][0], username)
            await ctx.send(file=discord.File(profileImage, "user_profile.png"))

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

    #@commands.command(aliases=["profilebg","profilebackground"], description="adds a custom profile background")
    #async def background(self, ctx: commands.Context):
    #    pass

async def setup(bot):
    await bot.add_cog(Database(bot))