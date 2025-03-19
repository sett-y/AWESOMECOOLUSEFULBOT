from discord.ext import bridge
import discord


async def send_message(ctx, message):
    if isinstance(ctx, bridge.BridgeExtContext):
        await ctx.send(message)
    elif isinstance(ctx, bridge.BridgeApplicationContext):
        await ctx.respond(message)

async def send_txt_file(ctx: bridge.BridgeContext, filepath):
    await ctx.respond(file=discord.File(filepath))
    #await ctx.respond(file=discord.File(filepath))