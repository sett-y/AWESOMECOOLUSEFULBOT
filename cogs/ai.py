from discord.ext import commands
import discord
import scripts.api as api
import os
import scripts.voicegen as voicegen

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["sp"], description="generate a response based on prompt given (history is per server)")
    async def prompt(self, ctx: commands.Context, *, arg):
        await ctx.send("generating response...")
        response = await api.serverPrompt(ctx, arg)
        if response:
            print("response generated")
            await ctx.send(response)

    @commands.command(name="fortune", description="prompt google gemini to generate a fortune")
    async def fortunecookie(self, ctx: commands.Context):
        await ctx.send("reading fortune...")
        fortune = await api.fortune()
        print("generated")
        await ctx.send(f"🥠 {fortune} 🥠")

    @commands.command(name="ascii", description="generate ascii art based on user prompt")
    async def asciiGen(self, ctx: commands.Context, *, arg):
        await ctx.send("generating ascii...")
        ascii = await api.asciiArt(arg)
        print("generated")
        await ctx.send(f"```{ascii}```")

    @commands.command(aliases=["gemini","ai"], description="generate a response based on prompt given")
    async def globalprompt(self, ctx: commands.Context, *, arg):
        await ctx.send("generating response...")
        try:
            response = await api.genericPrompt(ctx, arg)
        except Exception as e:
            print(e)
        if len(response) > 2000:
            print("response over 2000 character limit, writing to file")
            # load response into txt file
            async with open("response.txt", "w") as file:
                file.write(response)
            
            await ctx.send(file=discord.File("response.txt"))
            os.remove(f"{os.getcwd()}\\response.txt")
        else:
            print("response generated")
            await ctx.send(response)

    @commands.command()
    async def antiprompt(self, ctx: commands.Context, *, arg):
        await ctx.send("generating EVIL response...")
        response = await api.oppositePrompt(arg)
        print("response generated")
        await ctx.send(response)

    @commands.command()
    @commands.is_owner()
    async def globalhistory(self, ctx: commands.Context):
        history = await api.globalHistory()
        if not history:
            print("no prompt history available!")
            await ctx.send("no prompt history available!")
            return
        if len(history) > 2000:
            async with open("history.txt","w") as file:
                file.write(history)
            
            await ctx.send(file=discord.File("history.txt"))
            os.remove(f"{os.getcwd}\\history.txt")
        else:
            await ctx.send(history)

    @commands.command()
    @commands.is_owner()
    async def clearGlobalHistory(self, ctx: commands.Context):
        await api.clearGlobalHistory()

    @commands.command()
    @commands.is_owner()
    async def history(self, ctx: commands.Context):
        history = await api.serverHistory(ctx)
        if not history:
            return
        if len(history) > 2000:
            async with open("history.txt","w") as file:
                file.write(history)

            await ctx.send(file=discord.File("history.txt"))
            os.remove(f"{os.getcwd()}\\history.txt")
        else:
            await ctx.send(history)

    @commands.command()
    @commands.is_owner()
    async def clearServerHistory(self, ctx: commands.Context):
        await api.clearServerHistory(ctx)

    async def get_last_messages(self, ctx: commands.Context, n) -> list[str]:
        messages = []
        async for msg in ctx.channel.history(limit=int(n)):
            messageWithName = f"{msg.author.name}: {msg.content}"
            messages.append(messageWithName)
        messages.pop()
        messages.reverse()
        return messages

    @commands.command() 
    async def summarize(self, ctx: commands.Context, n: int):
        n = int(n)
        # check for valid user input
        if not isinstance(n, int) or n < 0:
            await ctx.send("the summarize command's parameter can only be a positive integer.")
            return

        messages = await self.get_last_messages(ctx, n)
        print("messages scraped")

        history = '\n'.join(str(x) for x in messages)

        await ctx.send("generating response...")
        response = await api.summarize(history)

        await ctx.send(response)

    @commands.command() # gemini image editing
    async def image(self, ctx: commands.Context, *, arg):
        pass

    @commands.command()
    async def voteclear(self, ctx: commands.Context):
        pass
        
    @commands.command(aliases=["vg"], description="""'af': 'Afrikaans', 'am': 'Amharic', 'ar': 'Arabic', 'bg': 'Bulgarian', 'bn': 'Bengali', 'bs': 'Bosnian', 'ca': 'Catalan', 'cs': 'Czech', 'cy': 'Welsh', 'da': 'Danish', 'de': 'German', 'el': 'Greek', 'en': 'English', 'es': 'Spanish', 'et': 'Estonian', 'eu': 'Basque', 'fi': 'Finnish', 'fr': 'French', 'fr-CA': 'French (Canada)', 'gl': 'Galician', 'gu': 'Gujarati', 'ha': 'Hausa', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 'id': 'Indonesian', 'is': 'Icelandic', 'it': 'Italian', 'iw': 'Hebrew', 'ja': 'Japanese', 'jw': 'Javanese', 'km': 'Khmer', 'kn': 'Kannada', 'ko': 'Korean', 'la': 'Latin', 'lt': 'Lithuanian', 'lv': 'Latvian', 'ml': 'Malayalam', 'mr': 'Marathi', 'ms': 'Malay', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'nl': 'Dutch', 'no': 'Norwegian', 'pa': 'Punjabi (Gurmukhi)', 'pl': 'Polish', 'pt': 'Portuguese (Brazil)', 'pt-PT': 'Portuguese (Portugal)', 'ro': 'Romanian', 'ru': 'Russian', 'si': 'Sinhala', 'sk': 'Slovak', 'sq': 'Albanian', 'sr': 'Serbian', 'su': 'Sundanese', 'sv': 'Swedish', 'sw': 
'Swahili', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tl': 'Filipino', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'vi': 'Vietnamese', 'yue': 'Cantonese', 'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Mandarin/Taiwan)', 'zh': 'Chinese (Mandarin)'""")
    async def voicegen(self, ctx: commands.Context, lang, *, arg):
        #if lang != ('com.au' and 'zh-CN'):
        #    await ctx.send("Language Invalid!")
        #    return
        await voicegen.main(arg, lang)
        await ctx.send(file=discord.File("scripts/voicegeneration/gen.mp3"))

    @commands.command(description="clears all gemini context history")
    @commands.is_owner()
    async def clear(self, ctx: commands.Context):
        pass

def setup(bot):
    bot.add_cog(AI(bot))