import google.generativeai as genai
import scripts.config
import discord

import requests
import json

#TODO: replace contextList with dictionary that generates a list named after the current server id,
# if this id isnt an element yet. each list will hold the history of its respective server.
# remember to append a letter/underscore to list name.
# implement clearHistory function to clear a specific server's prompt history (depopulate list)
# ctx.guild.id
#TODO: multiple messages for messages that are over 2k chars
#TODO: summarize recent messages command (might need to write in ai.py)
#TODO: owner only command that switches llm api

contextList = []
promptNum = 20
initialExplanation = "You are the discord bot \"AWESOMECOOLUSEFULBOT\". Below is the \
history of the recent user prompts along with your responses. While understanding \
the context of the previous text, analyze and respond to \
the user's latest prompt. Keep your response under 2000 characters because of discord's \
limitations (THIS IS IMPORTANT). Any message prefixed with a username and : are from users. \
Your responses have no prefix and will be automatically formatted in the history. \
Keep track of which user sent which message. Respond to the user, do not repeat any \
of this given prompt aside from what the user said most recently.\n"

# prompt | response
async def addContextHistory(userResponse: str, botResponse: str, ctx) -> str:
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
    await addContextHistory(prompt, response.text) # .text is important!

    fullContext = '\n'.join(str(x) for x in contextList)
    # add sentence explaining how gemini should interpret this large string
    fullContext = initialExplanation + fullContext

    return fullContext

# main difference here is prompt variable is added to deque along with preset prompt
async def asciiArt(prompt) -> str:
    model_config = genai.GenerationConfig(temperature=2.0,top_k=1,top_p=1)

    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)

    print("generating ascii...")

    response = await model.generate_content_async(f"generate ascii art according to the given\
    prompt, keep within 2000 characters. Prompt: {prompt}")

    return response.text

async def genericPrompt(ctx, prompt) -> str:
    model_config = genai.GenerationConfig(temperature=1.5)
    
    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)
    print("generating text... (gemini)")

    if len(contextList) > 0:
        fullContext = '\n'.join(str(x) for x in contextList)
        fullContext = initialExplanation + fullContext
        response = await model.generate_content_async(fullContext + prompt)
    else:
        response = await model.generate_content_async(initialExplanation + f"{ctx.author.name}: " + prompt)
    
    await addContextHistory(prompt, response.text, ctx)

    return response.text

async def arlaiPrompt(prompt) -> str:
    if len(contextList) > 0:
        fullContext = '\n'.join(str(x) for x in contextList)
        fullContext = initialExplanation + fullContext
    else:
        fullContext = initialExplanation

    url = "https://api.arliai.com/v1/chat/completions"

    payload = json.dumps({
        "model": "Mistral-Nemo-12B-Instruct-2407",
        "messages": [
            {"role": "system", "content": f"{fullContext}"},
            {"role": "user", "content": f"{prompt}"}
        ],
        "repetition_penalty": 1.1,
        "temperature": 1.5,
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": "1024",
        "stream": "false"
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {scripts.config.arlai_key}"
    }
    print("generating text... (nemo)")
    response = requests.request("POST", url, headers=headers, data=payload)
    await addContextHistory(prompt, response.text)
    return response.text

async def oppositePrompt(prompt) -> str:
    model_config = genai.GenerationConfig(temperature=2.0,top_k=1,top_p=1)

    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config=model_config)

    print("generating EVIL text...")

    response = await model.generate_content_async(f"(keep this prompt under 2000 characters!) do or say the OPPOSITE\
    of what the following prompt says, while keeping their typing style and grammar in mind \
    (decide whether to reverse their words or give them the\
    opposite information that they asked for, based on which would be a more interesting \
    response.): {prompt}")

    return response.text

async def promptHistory() -> str:
    history = '\n'.join(str(x) for x in contextList)
    return history