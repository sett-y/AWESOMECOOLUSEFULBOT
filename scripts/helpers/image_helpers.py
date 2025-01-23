from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands


async def check_image(ctx: commands.Context, url=None):
    if ctx.message.attachments:
        if ctx.message.attachments[0].filename.lower().endswith(('png','jpg','jpeg','webp','bmp')):
            attachment_file = ctx.message.attachments[0].url
            print("direct attachment")
            return attachment_file
    elif url:
        #TODO: image checks
        attachment_file = url
        print("url")
        return attachment_file
    else:
        print("no direct attachment or url in message")
        async for msg in ctx.channel.history(limit=20):
            # check if attachments exist, then check if attachment is img
            if msg.attachments:
                if msg.attachments[0].filename.lower().endswith(('png','jpg','jpeg','webp','bmp')):
                    return msg.attachments[0].url
            elif "http" in msg.content:
                msgContent = msg.content
                split = msgContent.split("http")
                splitEnd = split[1].split(" ")
                return "http" + splitEnd[0]
            else:
                print("invalid image")

async def load_image():
    pass