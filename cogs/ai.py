from discord.ext import commands
import discord
import scripts.api as api
import os
import scripts.voicegen as voicegen

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["serverprompt","p"], description="generate a response based on prompt given (history is per server)")
    async def prompt(self, ctx: commands.Context, *, arg):
        try:
            async with ctx.channel.typing():
                response = await api.serverPrompt(ctx, arg)
        except ValueError:
            await ctx.send("[message blocked retard]")
            print("message blocked")
        if response:
            print("response generated")
        else:
            return
        
        await self.sendResponse(ctx, response)
        
    @commands.command(aliases=["gemini","ai"], description="generate a response based on prompt given")
    async def globalprompt(self, ctx: commands.Context, *, arg):
        try:
            async with ctx.channel.typing():
                response = await api.genericPrompt(ctx, arg)
        except ValueError:
            await ctx.send("[message blocked retard]")
            print("message blocked")
        if response:
            print("response generated")
        else:
            return
        
        await self.sendResponse(ctx, response)

    @commands.command(aliases=["ap"], description="generate an EVIL response based on prompt given")
    async def antiprompt(self, ctx: commands.Context, *, arg):
        await ctx.send("generating EVIL response...")
        try:
            async with ctx.channel.typing():
                response = await api.oppositePrompt(arg)
        except ValueError:
            await ctx.send("[message blocked retard]")
            print("message blocked")
        if response:
            print("response generated")
        else:
            return
        
        await self.sendResponse(ctx, response)
    
    # checks if response is over 2k chars and loads / sends txt file, otherwise sends normally
    async def sendResponse(self, ctx: commands.Context, response):
        if len(response) > 2000:
            print("response over 2000 character limit, writing to file")
            # load response into txt file
            with open("response.txt","w") as file:
                file.write(response)
            
            await ctx.send(file=discord.File("response.txt"))
            os.remove(f"response.txt")
        else:
            await ctx.send(response)

    @commands.command(name="fortune", description="prompt google gemini to generate a fortune")
    async def fortunecookie(self, ctx: commands.Context):
        await ctx.send("reading fortune...")
        try:
            async with ctx.channel.typing():
                fortune = await api.fortune()
        except ValueError:
            await ctx.send("[message blocked retard]")
            print("message blocked")
        print("generated")
        await ctx.send(f"🥠 {fortune} 🥠")

    @commands.command(name="ascii", description="generate ascii art based on user prompt")
    async def asciiGen(self, ctx: commands.Context, *, arg):
        await ctx.send("generating ascii...")
        ascii = await api.asciiArt(arg)
        print("generated")
        await ctx.send(f"```{ascii}```")

    @commands.command(description="global context history (owner only)")
    @commands.is_owner()
    async def globalhistory(self, ctx: commands.Context):
        history = await api.globalHistory()
        if not history:
            print("no global prompt history available!")
            await ctx.send("no global prompt history available!")
            return
        if len(history) > 2000:
            with open("history.txt","w") as file:
                file.write(history)
            
            await ctx.send(file=discord.File("history.txt"))
            os.remove(f"history.txt")
        else:
            await ctx.send(history)

    @commands.command(aliases=["cgh"])
    @commands.is_owner()
    async def clearglobalhistory(self, ctx: commands.Context):
        await api.clearGlobalHistory()
        await ctx.send("global history cleared")

    @commands.command(description="server context history")
    async def history(self, ctx: commands.Context):
        history = await api.serverHistory(ctx)
        if not history:
            print("no prompt history available!")
            await ctx.send("no prompt history available!")
            return
        if len(history) > 2000:
            with open("history.txt","w") as file:
                file.write(history)

            await ctx.send(file=discord.File("history.txt"))
            os.remove(f"history.txt")
        else:
            await ctx.send(history)

    @commands.command(aliases=["csh"])
    @commands.is_owner()
    async def clearserverhistory(self, ctx: commands.Context):
        await api.clearServerHistory(ctx)
        await ctx.send("server history cleared")

    async def get_last_messages(self, ctx: commands.Context, n) -> list[str]:
        messages = []
        async for msg in ctx.channel.history(limit=int(n)):
            messageWithName = f"{msg.author.name}: {msg.content}"
            messages.append(messageWithName)
        messages.pop() # removes prompt command message since prompt is already sent
        messages.reverse()
        return messages

    @commands.command(description="google gemini summarizes N recent chat messages")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def summarize(self, ctx: commands.Context, n: int):
        n = int(n)
        # check for valid user input
        if not isinstance(n, int) or n < 0:
            await ctx.send("parameter can only be a positive integer.")
            return
        
        if n > 1000:
            await ctx.send("no")
            return
        
        async with ctx.channel.typing():
            messages = await self.get_last_messages(ctx, n)
            print("messages scraped")

            history = '\n'.join(str(x) for x in messages)
        
            response = await api.summarize(history)

        if len(response) > 2000 and len(response) < 8000:
            with open("summary.txt","w") as file:
                file.write(response)
            await ctx.send(file=discord.File("summary.txt"))
            os.remove(f"{os.getcwd()}\\summary.txt")
        elif len(response) < 2000:
            await ctx.send(response)
        else:
            await ctx.send("too dam long idiot")

    # votes to clear server context history
    #@commands.command()
    #async def voteclear(self, ctx: commands.Context):
    #    pass
        
    @commands.command(aliases=["vg"], description="""'af': 'Afrikaans', 'am': 'Amharic', 'ar': 'Arabic', 'bg': 'Bulgarian', 'bn': 'Bengali', 'bs': 'Bosnian', 'ca': 'Catalan', 'cs': 'Czech', 'cy': 'Welsh', 'da': 'Danish', 'de': 'German', 'el': 'Greek', 'en': 'English', 'es': 'Spanish', 'et': 'Estonian', 'eu': 'Basque', 'fi': 'Finnish', 'fr': 'French', 'fr-CA': 'French (Canada)', 'gl': 'Galician', 'gu': 'Gujarati', 'ha': 'Hausa', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 'id': 'Indonesian', 'is': 'Icelandic', 'it': 'Italian', 'iw': 'Hebrew', 'ja': 'Japanese', 'jw': 'Javanese', 'km': 'Khmer', 'kn': 'Kannada', 'ko': 'Korean', 'la': 'Latin', 'lt': 'Lithuanian', 'lv': 'Latvian', 'ml': 'Malayalam', 'mr': 'Marathi', 'ms': 'Malay', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'nl': 'Dutch', 'no': 'Norwegian', 'pa': 'Punjabi (Gurmukhi)', 'pl': 'Polish', 'pt': 'Portuguese (Brazil)', 'pt-PT': 'Portuguese (Portugal)', 'ro': 'Romanian', 'ru': 'Russian', 'si': 'Sinhala', 'sk': 'Slovak', 'sq': 'Albanian', 'sr': 'Serbian', 'su': 'Sundanese', 'sv': 'Swedish', 'sw': 
'Swahili', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tl': 'Filipino', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'vi': 'Vietnamese', 'yue': 'Cantonese', 'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Mandarin/Taiwan)', 'zh': 'Chinese (Mandarin)'""")
    async def voicegen(self, ctx: commands.Context, lang, *, message):
        async with ctx.channel.typing():
            await voicegen.main(message, lang)
            await ctx.send(file=discord.File("scripts/voicegeneration/gen.mp3"))

    @commands.command(description="clears all gemini context history")
    @commands.is_owner()
    async def clear(self, ctx: commands.Context):
        pass

    @commands.command(aliases=["sp"])
    async def singleprompt(self, ctx: commands.Context, *, arg):
        try:
            async with ctx.channel.typing():
                response = await api.singlePrompt(arg)
        except ValueError:
            await ctx.send("[message blocked retard]")
            print("message blocked")

        await self.sendResponse(ctx, response)

def setup(bot):
    bot.add_cog(AI(bot))