from PIL import Image
from discord.ext import commands
from typing import Optional
import io


async def check_image(ctx: commands.Context, url=None) -> Optional[str]:
    if ctx.message.attachments:
        if ctx.message.attachments[0].filename.lower().endswith(('png','jpg','jpeg','webp','bmp','gif')):
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
        try:
            async for msg in ctx.channel.history(limit=40):
                # check if attachments exist, then check if attachment is img
                if msg.attachments:
                    if msg.attachments[0].filename.lower().endswith(('png','jpg','jpeg','webp','bmp','gif')):
                        return msg.attachments[0].url
                elif "http" in msg.content:
                    msgContent = msg.content
                    split = msgContent.split("http")
                    splitEnd = split[1].split(" ")
                    return "http" + splitEnd[0]
                else:
                    print("invalid image")
                    # NO RETURN HERE
        except Exception as e:
            print(e)


async def imageCheck(ctx: commands.Context, session):
    if ctx.message.attachments:
        imgUrl = ctx.message.attachments[0].url
        print("prompt has attachment")
    elif "http" in ctx.message.content:
        content = ctx.message.content
        httpContent = content.split("http")
        splitContent = httpContent[1].split(" ")
        imgUrl = "http" + splitContent[0]
        print("prompt has url")
    else:
        print("no attachment")
        return

    async with session.get(imgUrl) as attach:
        if attach.status != 200:
            print("failed to fetch image")
            return
        imageData = await attach.read()
        img = Image.open(io.BytesIO(imageData))
        return img