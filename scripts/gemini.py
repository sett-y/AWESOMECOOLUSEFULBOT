import google.generativeai as genai
import scripts.config

async def fortune():
    model_config = genai.GenerationConfig(temperature=2.0,top_k=1,top_p=1)

    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-1.5-flash", generation_config=model_config)
    print("generating...")
    response = await model.generate_content_async("write a fortune one would find in a fortune cookie.\
    try to make it creative, some of the advice should be somewhat specific. talk like a pirate. add\
    a few random chinese characters in the middle of the fortune.")

    return response.text

async def asciiArt(prompt):
    model_config = genai.GenerationConfig(temperature=2.0,top_k=1,top_p=1)

    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-1.5-flash", generation_config=model_config)

    print("generating ascii...")

    response = await model.generate_content_async(f"generate ascii art according to the given\
    prompt, keep within 2000 characters. Prompt: {prompt}")

    return response.text

async def genericPrompt(prompt):
    genai.configure(api_key=scripts.config.genai_token)
    model = genai.GenerativeModel("gemini-1.5-flash")

    print("generating text...")

    response = await model.generate_content_async(f"{prompt} (keep this prompt under 2000 characters)")

    return response.text    