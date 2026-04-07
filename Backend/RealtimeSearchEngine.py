from googlesearch import search
from groq import Groq   #importing the groq library
from json import load, dump
import datetime
from dotenv import dotenv_values
from ddgs import DDGS

#load env variable from .env file.
env_vars = dotenv_values(".env")

# Retrive environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

#initialize the groq client with the provided API Key.
client = Groq(api_key=GroqAPIKey)

# Define the System instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try to load the chat log from a json file, or create an empty one if not exist.
try:
    with open(r"Data\ChatLog.json","r") as f:
        messages = load(f)
except:
    with open(r"Data|ChatLog.json","w") as f:
        dump([],f)
    
def GoogleSearch(query):
    ddgs = DDGS()
    results = ddgs.text(query, max_results=5)

    # Collect only the descriptions (no links/titles)
    descriptions = [r['body'] for r in results if 'body' in r and r['body']]

    if not descriptions:
        return f"No clear results found for '{query}'."

    # Combine descriptions into one text block
    raw_text = "\n".join(descriptions)

    # Return raw text (this will later be summarized by your LLM)
    Answer = f"The search result for '{query}' are:\n[start]\n{raw_text}\n[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modifier_answer = '\n'.join(non_empty_lines)
    return modifier_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can i help you?"}
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hour,{minute} minute, {second} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages
    
    with open(r"Data\ChatLog.json","r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": f"{prompt}"})
    
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})
    
    completion = client.chat.completions.create(
        model="llama-3.3-70B-versatile",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )
    
    Answer = ""
    
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
            
    Answer = Answer.strip().replace("</s>","")
    messages.append({"role": "assistant", "content": Answer})
    
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)
        
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))