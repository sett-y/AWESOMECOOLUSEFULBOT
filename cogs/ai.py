from discord.ext import commands
import scripts.api as api


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fortune", description="prompt google gemini to generate a fortune")
    async def fortunecookie(self, ctx):
        await ctx.send("reading fortune...")
        fortune = await api.fortune()
        print("generated")
        await ctx.send(f"🥠 {fortune} 🥠")

    @commands.command(name="ascii", description="generate ascii art based on user prompt")
    async def asciiGen(self, ctx, *, arg):
        await ctx.send("generating ascii...")
        ascii = await api.asciiArt(arg)
        print("generated")
        await ctx.send(f"```{ascii}```")

    @commands.command(name="prompt", description="generate a response based on prompt given")
    async def prompt(self, ctx, *, arg):
        await ctx.send("generating response...")
        try:
            response = await api.genericPrompt(ctx, arg)
        except Exception as e:
            print(e)
        if len(response) > 2000:
            print("response is over the 2000 character limit, splitting string")
            response1 = response[:2000]
            response2 = response[2000:]
            await ctx.send(response1)
            await ctx.send(response2)
        else:
            print("response generated")
            await ctx.send(response)

    @commands.command(name="tempprompt")
    async def tempPrompt(self, ctx, *, arg):
        await ctx.send("generating response... (arlai)")
        response = await api.arlaiPrompt(arg)
        if len(response) > 2000:
            print("response is over the 2000 character limit, truncating")
            response = response[:2000]
        print("response generated")
        await ctx.send(response)

    @commands.command()
    async def antiprompt(self, ctx, *, arg):
        await ctx.send("generating EVIL response...")
        response = await api.oppositePrompt(arg)
        print("response generated")
        await ctx.send(response)

    @commands.command()
    @commands.is_owner()
    async def history(self, ctx):
        history = await api.promptHistory()
        if not history:
            print("no prompt history available!")
            await ctx.send("no prompt history available!")
            return
        if len(history) > 2000:
            history = history[:2000]
        await ctx.send(history)

    @commands.command()
    async def summarize(self, ctx, numMsg):
        await ctx.send(numMsg)

async def setup(bot):
    await bot.add_cog(AI(bot))