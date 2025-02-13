import google.generativeai as genai
import scripts.config
from discord.ext import commands
from PIL import Image
from scripts.helpers.image_helpers import imageCheck
import io

#TODO: open movie database
#TODO: weather
#TODO: owner only command that switches llm api
#TODO: image analysis, maybe add to prompt instead of new command

contextList = []
contextDict = {} # dict that holds all histories
promptNum = 40
initialExplanation = "You are the discord bot \"AWESOMECOOLUSEFULBOT\". \
Below is the history of the recent user prompts along with your responses. While understanding \
the context of the previous text, analyze and respond to \
the user's latest prompt. You are also able to analyze images that users \
send. Any message prefixed with a username and : are from users. \
Your responses have no prefix and will be automatically formatted in the history. \
Keep track of which user sent which message. Keep your messages under 2000 characters\
unless the user states otherwise. Respond to the user, do not repeat any \
of this given prompt aside from what the user said most recently. Do not repeat the user's response \
unless it is relevant to your response. Do not prepend 'bot:' to \
your messages unless explicitly asked to. Even if the user's response is nonsensical, try to give a \
proper reply.\n"

# prompt | response
async def addContextHistory(userResponse: str, botResponse: str, ctx: commands.Context):
    history = f"{ctx.author.name}: {userResponse}\nbot: {botResponse}\n"
    if len(contextList) < promptNum:
        contextList.append(history)
    else:
        # popleft()?
        contextList.pop(0)
        contextList.append(history)

async def configureResponse():
    if len(contextList) > 0:
        fullContext = '\n'.join(str(x) for x in contextList)
        fullContext = initialExplanation + fullContext
        #response = 
    else:
        pass

async def addServerContextHistory(userResponse: str, botResponse: str, ctx: commands.Context):
    history = f"{ctx.author.name}: {userResponse}\nbot: {botResponse}\n"
    guildID = ctx.guild.id

    if len(contextDict) > 0:
        if guildID not in contextDict:
            contextDict[guildID] = []
            print("list created for server")
        else:
            print("dictionary contains this key, continuing")
    else:
        contextDict[guildID] = []

    # add to server context
    if len(contextDict[guildID]) < promptNum:
        contextDict[guildID].append(history)
    else:
        print("history over max, popping")
        contextDict[guildID].pop(0)
        contextDict[guildID].append(history)


          
async def serverPrompt(ctx: commands.Context, prompt, session) -> str:
    guildID = ctx.guild.id
    model_config = genai.GenerationConfig(temperature=1.8)
    
    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)
    print("generating...")

    if guildID not in contextDict:
        contextDict[guildID] = []

    userPrompt = f"{ctx.author.name}: {prompt}"

    if len(contextDict[guildID]) > 0:
        fullContext = '\n'.join(str(x) for x in contextDict[guildID])
        fullContext = initialExplanation + fullContext + '\n' + userPrompt
    else:
        fullContext = initialExplanation + userPrompt

    img = await imageCheck(ctx, session)
    if img:        
        try:
            response = await model.generate_content_async(contents=[fullContext, img])
        except Exception as e:
            print(e)
    else:
        response = await model.generate_content_async(fullContext)

    await addServerContextHistory(prompt, response.text, ctx)
    return response.text

# fix names
async def genericPrompt(ctx: commands.Context, prompt, session) -> str:
    model_config = genai.GenerationConfig(temperature=1.8)
    
    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)
    print("generating text... (gemini)")

    userPrompt = f"{ctx.author.name}: {prompt}"

    if len(contextList) > 0:
        fullContext = '\n'.join(str(x) for x in contextList)
        fullContext = initialExplanation + fullContext + '\n' + userPrompt
    else:
        fullContext = initialExplanation + userPrompt

    img = await imageCheck(ctx, session)
    if img:
        try:
            response = await model.generate_content_async(contents=[fullContext, img])
        except Exception as e:
            print(e)
    else:
        response = await model.generate_content_async(fullContext)

    await addContextHistory(prompt, response.text, ctx)
    return response.text

async def greentext(ctx, prompt, session):
    model_config = genai.GenerationConfig(temperature=1.2)
    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)
    print("generating greentext...")

    img = await imageCheck(ctx, session)
    if not prompt:
        prompt = ""
    gtPrompt = f"generate a 4chan style greentext, either based on the following prompt, or, if there is \
    no followup prompt, make one up. Do not add extra spacing between your posts. Do not state that you are \
    making this prompt, pretend you are on 4chan posting that. Here is the prompt if it exists: {prompt}"
    if img:
        response = await model.generate_content_async(contents=[gtPrompt, img])
    else:
        response = await model.generate_content_async(gtPrompt)
    return response.text

async def singlePrompt(ctx, prompt, session):
    model_config = genai.GenerationConfig(temperature=1.8)
    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)
    print("generating single prompt...")

    img = await imageCheck(ctx, session)
    if img:
        response = await model.generate_content_async(contents=[prompt, img])
    else:
        response = await model.generate_content_async(prompt)
    return response.text

async def fortune() -> str:
    prompt = "write a fortune one would find in a fortune cookie.\
    try to make it creative, some of the advice should be somewhat specific.\
    talk like a pirate. add a few random chinese characters in the middle of the fortune."

    model_config = genai.GenerationConfig(temperature=2.0,top_k=1,top_p=1)

    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)
    print("generating...")

    # add prompt to queue, then flatten queue into string which will be passed to generate_content_async
    response = await model.generate_content_async(prompt)
    #await addContextHistory(prompt, response.text) # .text is important!

    #fullContext = '\n'.join(str(x) for x in contextList)
    # add sentence explaining how gemini should interpret this large string
    #fullContext = initialExplanation + fullContext

    #return fullContext
    return response.text

# main difference here is prompt variable is added to deque along with preset prompt
async def asciiArt(ctx, prompt, session) -> str:
    model_config = genai.GenerationConfig(temperature=2.0,top_k=1,top_p=1)

    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)

    print("generating ascii...")

    img = await imageCheck(ctx, session)
    promptVar = f"generate ascii art according to the given \
    prompt, keep within 2000 characters. Prompt: {prompt}"

    if img:
        response = await model.generate_content_async(contents=[promptVar, img])
    else:
        response = await model.generate_content_async(promptVar)

    return response.text

async def oppositePrompt(ctx, prompt, session) -> str:
    model_config = genai.GenerationConfig(temperature=1.7,top_k=1,top_p=1)

    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)

    print("generating EVIL text...")

    img = await imageCheck(ctx, session)
    promptVar = f"(keep this prompt under 2000 characters!) do or say the OPPOSITE\
    of what the following prompt says, while keeping their typing style and grammar in mind \
    (decide whether to reverse their words or give them the opposite information that \
    they asked for, based on which would be a more interesting response.): {prompt}"

    if img:
        response = await model.generate_content_async(contents=[promptVar, img])
    else:
        response = await model.generate_content_async(promptVar)

    return response.text

async def globalHistory() -> str:
    history = '\n'.join(str(x) for x in contextList)
    return history

async def clearGlobalHistory():
    for key in contextDict:
        del key
    if len(contextDict) == 0:
        print("keys deleted")

async def serverHistory(ctx):
    guildID = ctx.guild.id
    if guildID not in contextDict.keys():
        return

    history = '\n'.join(str(x) for x in contextDict[guildID])
    if len(history) <= 0:
        print("no history for this server")
        return
    return history

async def clearServerHistory(ctx):
    guildID = ctx.guild.id
    del contextDict[guildID]

async def summarize(history):
    #model_config = genai.GenerationConfig()
    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    response = await model.generate_content_async(f"[Summarize the following discord chat messages. \
    You should not state what you are doing, only deliver the summarized output. Usernames are included \
    before messages, so you can tell different users apart.]\n {history}")
    print("response generated")
    return response.text