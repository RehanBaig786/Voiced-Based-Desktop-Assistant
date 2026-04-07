from AppOpener import open as appopen
from AppOpener import close, give_appnames
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Backend')))
from TextToSpeech import TTS

from TextToSpeech import TTS

#load evironment variables from the .env file.
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

#defien css classes for parsing specific ele in html content.
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", 
           "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

#define user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/100.0.4896.75 Safari/537.36'

#intialize the Groq client with the API Key.
client = Groq(api_key=GroqAPIKey)

#predifined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anyhting else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]

#list to store Chatbot messages.
messages=[]

# System msg to provid context to the chatbot.
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letter."}]

#func to perform a Google search
def GoogleSearch(Topic):
    search(Topic)  # Use pywhatkit's search func to perform a google search.
    return True  #indicate success.

#func to generate content using Ai and save it to file.
def Content(Topic):
    
    #Nested func to open a file in Notepad
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe' #default txt editor.
        subprocess.Popen([default_text_editor, File]) #open the file in Notepad.
        
    #Nested func to generate content using the Ai chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})  #add the user's prompt to msg's.
        
        completion = client.chat.completions.create(
            model="llama-3.3-70B-versatile",  #specify the AI model.
            messages=SystemChatBot + messages,  # include system instruction and chat history.
            max_tokens=2048,  #limit the maximum tokens i the response
            temperature=0.7,  #adjust response randomness.
            top_p=1,  #use sampling for response diversity.
            stream=True,  #enable streaming response.
            stop= None  #Allow the model to determine stooping conditions.
        ) 
        
        Answer = ""  #initialize an empty string for response.
        
        #process streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:  #check for content in current chunk
                Answer += chunk.choices[0].delta.content  #Append the content to the answer.
                
        Answer = Answer.replace("</s>","")  #remove unwanted tokens from response
        messages.append({"role": "assistant", "content": Answer})  #Add the Ai's response to msg.
        return Answer
        
    Topic: str = Topic.replace("Content ","")  #remove "Content " from the topic
    ContentByAI = ContentWriterAI(Topic)  #generate content using AI
    
    #Save the generated content to a text file.
    with open(rf"Data\{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()
        
    OpenNotepad(rf"Data\{Topic.lower().replace(' ','')}.txt")  #open the file in Notepad.
    return True  #indicate success

#function to search for a topic on youtube
def YoutubeSearch(Topic: str):
    try:
        Topic = Topic.strip().replace(" ", "+")  # format query properly
        Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
        print(f"[green]Opening YouTube search for: {Topic}[/green]")
        webbrowser.open(Url4Search)  # open in default browser
        return True
    except Exception as e:
        print(f"[red]YouTube search failed: {e}[/red]")
        return False


#function to play a vedio on YouTube.
def PlayYoutube(query):
    playonyt(query)  #use pywhatkit's playonyt func
    return True  #indicate success

APP_WEBSITES = {
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "telegram": "https://telegram.org",
    "spotify": "https://www.spotify.com",
    "unreal engine": "https://www.unrealengine.com",
    "twitter": "https://twitter.com",
    "snapchat": "https://www.snapchat.com",
    "zoom": "https://zoom.us",
    "discord": "https://discord.com",
    "linkedin": "https://www.linkedin.com",
    "canva": "https://www.canva.com",
}

#function to oprn an app or a relavant webpage.
def OpenApp(app, sess=requests.session()):
    app = app.lower().strip()
    with open(r'Frontend/Files/Response.data', 'w', encoding='utf-8') as f:
        f.write(f"Elaris : Opening {app}")
    TTS(f"Opening {app}")

    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"[green]Opened installed app: {app}[/green]")
        return True
    except Exception as e:
        print(f"[yellow]App '{app}' not found. Trying to open website...[/yellow]")

        # Check known app-to-website mapping
        for known_app in APP_WEBSITES:
            if known_app in app:
                print(f"[green]Opening official site: {APP_WEBSITES[known_app]}[/green]")
                webopen(APP_WEBSITES[known_app])
                return True

        # If not in known apps, fallback to Google search
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        def extract_links(html):
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', href=True)
            return [link.get('href') for link in links if link.get('href').startswith("http")]

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                print(f"[cyan]Opening top search result: {links[0]}[/cyan]")
                webopen(links[0])
                return True

        print(f"[red]Unable to open '{app}' via app or web.[/red]")
        return False

    
#func to close an app.
# def CloseApp(app):
    
#     if "chrome" in app:
#         pass  #skip if the app is chrome.
#     else:
#         try:
#             close(app, match_closest=True, throw_error=True) #attempt to close the app.
#             return True
#         except:
#             return False  # Indicate failure
def CloseApp(app):
    app = app.lower().strip()

    if "chrome" in app:
        print("[yellow]Skipping Chrome closure[/yellow]")
        return False

    try:
        # First try AppOpener
        close(app, match_closest=True, throw_error=True)
        print(f"[green]Closed {app} successfully using AppOpener[/green]")
        return True
    except Exception as e:
        print(f"[yellow]AppOpener failed for {app}: {e}[/yellow]")
        
        # Fallback: try killing the process via taskkill
        try:
            subprocess.run(f"taskkill /f /im {app}.exe", shell=True, capture_output=True)
            print(f"[green]Closed {app} using taskkill[/green]")
            return True
        except Exception as e2:
            print(f"[red]Failed to close {app}: {e2}[/red]")
            return False
        
# func to execute system-level commands.
def System(command):
    
    #nested func to mute the sys vol.
    def mute():
        keyboard.press_and_release("volume mute")  #simulate mute the sys vol.
        
    #nested func to unmute the sys vol.
    def unmute():
        keyboard.press_and_release("volume mute")  #simulate to unmute the sys vol.
        
    #nested func to increase the sys vol.
    def volume_up():
        keyboard.press_and_release("volume up")  #simulate to volume the sys vol.
        
    #nested func to decrease the sys vol.
    def volume_down():
        keyboard.press_and_release("volume down")  #simulate to volume the sys vol.
        
    #Execute the appropriate command.
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
        
    return True  #Indicate success.
    
#Asynchronous func to translte and execute user command
async def TranslateAndExecute(commands: list[str]):
    
    funcs = []  #List to store asynchronous tasks.
    
    for command in commands:
        
        if command.startswith("open "):  #handle "open command"
            if "open it" in command:  # Ignore "open it" command
                pass
            
            if "open file" == command:  #ignore "open file" commands.
                pass
            
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))  #schedule app opening
                funcs.append(fun)
                
        elif command.startswith("general "):  #placeholder for general commands.
            pass
        
        elif command.startswith("close "):  #Handle "close" commands.
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))  #schedule app closing.
            funcs.append(fun)
            
        elif command.startswith("play "): #Handle "play " commands.
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))  #schedule youtube playback.
            funcs.append(fun)
            
        elif command.startswith("content "): #handle "content" commands.
            fun = asyncio.to_thread(Content, command.removeprefix("content "))  #schedule content creation.
            funcs.append(fun)
            
        elif command.startswith("google search "):  #handle google search commands.
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")) #schedule google search.
            funcs.append(fun)
            
        elif command.startswith("youtube search "):  #handle youtube search commands.
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search ")) #schedule youtube search.
            funcs.append(fun)
            
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
            
        else:
            print(f"No Function Found. For {command} ")  #print an error for unrecognized commands.
            
    results = await asyncio.gather(*funcs)  #execute all tasks concurently.
    
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result
            
#Asynchronous func to automate command execution.
async def Automation(commands: list[str]):
    
    async for result in TranslateAndExecute(commands):
        pass
    
    return True  #indicate success.

if __name__ == "__main__":
    # asyncio.run(Automation(["open facebook", "open instagram", "open telegram", "youtube","play afsanay", "content song for me"]))
    asyncio.run(Automation([ "open Canva editer"]))