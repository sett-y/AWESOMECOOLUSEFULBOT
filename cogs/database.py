from discord.ext import commands
import discord
import traceback
from PIL import Image, ImageDraw, ImageFont
import io
#from scripts.helpers.db_helpers import update_column


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        print(wrappedMessage)
        return wrappedMessage, numOfLines

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

                # bio text
                bbox = bioImage.textbbox((0,0), text, font)
                bioWidth = bbox[2] - bbox[0]
                bioHeight = bbox[3] - bbox[1]
                bioX, bioY = 50, 50

                text, lineMult = await self.textWrap(message=text, maxLen=20)

                bioRec = [
                    (bioX, bioY),
                    (bioX + bioWidth, (bioY + bioHeight + 7)*lineMult)
                ]
                bioImage.rectangle(bioRec, outline="white")
                bioImage.text((bioX,bioY), text=text, font=font)

                # username text
                bioImage.text((100,100), text=username, font=font)
                # box for username
                #bioImage

                paste_width, paste_height = avatarImage.size
                x = (base_width - paste_width) // 2
                y = (base_height - paste_height) // 2

                baseImage.paste(avatarImage, (x,y))

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


def setup(bot):
    bot.add_cog(Database(bot))