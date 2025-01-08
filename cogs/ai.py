from discord.ext import commands
import discord
import scripts.api as api
import os


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(aliases=["prompt","gemini","ai"], description="generate a response based on prompt given")
    async def promptGemini(self, ctx: commands.Context, *, arg):
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
    async def history(self, ctx: commands.Context):
        history = await api.promptHistory()
        if not history:
            print("no prompt history available!")
            await ctx.send("no prompt history available!")
            return
        if len(history) > 2000:
            async with open("history.txt", "w") as file:
                file.write(history)
            
            await ctx.send(file=discord.File("history.txt"))
            os.remove(f"{os.getcwd}\\history.txt")
        else:
            await ctx.send(history)

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
        

def setup(bot):
    bot.add_cog(AI(bot))