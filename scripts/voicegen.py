import gtts

async def main(text, lang):
    try:
        myobj = gtts.gTTS(text=text, lang=lang,tld='com', slow=False)
    except Exception as e:
        print(e)
    #fart = gtts.lang.tts_langs()
    myobj.save("scripts/voicegeneration/gen.mp3")
    