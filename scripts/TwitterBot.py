from atproto import AsyncClient, client_utils
import os
from scripts.config import bsky_username, bsky_password
import re

client = AsyncClient()

# bluesky demands images/videos to be uploaded as binary blobs
async def postMessage(message=None, attachment=None, username=None):
    await client.login(login=bsky_username,password=bsky_password)
    # filter bad words
    badword = r"n+i+g+e+r+"
    message = re.sub(badword,"friend",message,flags=re.IGNORECASE)
    #TODO for loop checking for multiple words

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
    profile = await client.get_author_feed(actor="awesomecoolbot.bsky.social",limit=1)
    name = "awesomecoolbot.bsky.social"
    full_post_uri = profile.feed[0]
    post_uri = full_post_uri.post.uri.split('post/')[-1]
    post_url = f"https://bsky.app/profile/{name}/post/{post_uri}"
    
    return post_url