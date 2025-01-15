from atproto import AsyncClient, client_utils
import os
from scripts.config import bsky_username, bsky_password


client = AsyncClient()

# bluesky demands images/videos to be uploaded as binary blobs
async def postMessage(message=None, attachment=None, username=None):
    await client.login(login=bsky_username,password=bsky_password)

    if message and attachment:# text and image/video
        with open(attachment,'rb') as file:
            image_data = file.read()
        await client.send_image(text=message,image=image_data, image_alt=username)
    
    elif attachment:#image/video
        with open(attachment,'rb') as file:
            image_data = file.read()
        await client.send_image(image=image_data,text="",image_alt=username)
    
    elif message:#text
        await client.send_post(text=message)

    if attachment:
        os.remove(attachment)


async def getLastPost():
    #profile = 
    await client.login(login=bsky_username,password=bsky_password)
    bsky_posts = client.get_posts()
    