from google import genai
from google.genai import types

from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = "You must generate a short and concise response to the following scenario in english. I want the response to be eloquent, sophisticated, and imaginative."

def birthday_text():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            thinking_config=types.ThinkingConfig(thinking_budget=0)),
        
        contents=["Generate a short birthday message. Do not add punctuation to the end of the sentence."]
        )
    
    return response.text
    