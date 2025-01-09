from gtts import gTTS
import gtts
import os
import asyncio

async def main(text, lang, tld=''):
    text = text
    language = lang
    #tld = tld
    # Language in which you want to convert
    myobj = gTTS(text=text, lang=language,tld='com', slow=False)
    fart = gtts.lang.tts_langs()
    # Saving the converted audio in a mp3 file named
    # welcome 
    myobj.save("scripts/voicegeneration/gen.mp3")
    