from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def helpswitch(self, ctx, arg):
        #declare embed here and append description via cases
        match arg:
            case "prompt":
                embed = discord.Embed(title=">prompt",
                                      description="prompt help",
                                      color=0x98FB98)
                await ctx.send(content="test embed", embed=embed)
            case "reminder":
                print("reminder")
            case "reload":
                print("reload")
            case "vcsong":
                print("vcsong")
            case "echo":
                print("echo")
            case "commandlist":
                print("commandlist")
            case "shutdown":
                print("shutdown")
            case "help":
                pass
            case "joinDate":
                pass
            case "restart":
                pass
            case "display_profile":
                pass
            case "pfp":
                pass
            case "catfact":
                pass
            case "display_match":
                pass
            case "weather":
                pass
            case "mp3":
                pass
            case "mp4":
                pass
            case "delivery_notif":
                pass
            case "fortune":
                pass
            case "servpic":
                pass
            case "website":
                pass
            case "troll":
                pass
            case "ascii":
                pass

            
        


async def setup(bot):
    await bot.add_cog(Help(bot))