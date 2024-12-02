from discord.ext import commands
import scripts.gemini as gemini


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fortune", description="prompt google gemini to generate a fortune")
    async def fortunecookie(self, ctx):
        await ctx.send("reading fortune...")
        fortune = await gemini.fortune()
        print("generated")
        await ctx.send(f"🥠 {fortune} 🥠")


    @commands.command(name="ascii", description="generate ascii art based on user prompt")
    async def asciiGen(self, ctx, *, arg):
        await ctx.send("generating ascii...")
        ascii = await gemini.asciiArt(arg)
        print("generated")
        await ctx.send(f"```{ascii}```")


    @commands.command(name="prompt", description="generate a response based on prompt given")
    async def prompt(self, ctx, *, arg):
        await ctx.send("generating response...")
        response = await gemini.genericPrompt(arg)
        print("response generated")
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(AI(bot))