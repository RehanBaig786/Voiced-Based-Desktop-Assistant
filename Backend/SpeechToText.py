from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

env_vars = dotenv_values(".env")

InputLangauge = env_vars.get("InputLangauge")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''


HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLangauge}';")

# write the modified HTML code to a file.
with open(r"Data\Voice.html","w") as f:
    f.write(HtmlCode)
    
currrent_dir = os.getcwd()

Link = f"{currrent_dir}/Data/Voice.html"

chrome_options = Options()

prefs = {
    "profile.default_content_setting_values.media_stream_mic": 1,  # 1 = Allow
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1,
    "profile.default_content_setting_values.notifications": 1
}
chrome_options.add_experimental_option("prefs", prefs)
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36(KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--user-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

#initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# define path for temporary files.
TempDirPath = rf"{currrent_dir}/Frontend/Files"

#function to set the assistant status by writtting it to a file.
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data',"w", encoding='utf-8') as file:
        file.write(Status)
        
#function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how","what","who","where","when","why","which","whose","whom","can you","what's","where's","how's","can you"]

    #check if the query is a question and add a question mark if necessary.
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        #Add a period if the query is not a question
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
        
    return new_query.capitalize()

#to translte text into eng using mtranslate library.
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

#func to perform speech recognition using the WebDriver.
def SpeechRecognition():
    #open the html file in the browser.
    driver.get("file:///" + Link)
    #start speech recognition by clicking the start button.
    driver.find_element(by=By.ID, value="start").click()
    
    while True:
        try:
            #get the recognized text from the html o/p element.
            Text = driver.find_element(by=By.ID, value="output").text
            
            if Text:
                #stop recognition by clicking the stop button.
                driver.find_element(by=By.ID, value="end").click()
                
                #if the i/p lang is eng, return the modifier query.
                if InputLangauge.lower() == "en" or "en" in InputLangauge.lower():
                    return QueryModifier(Text)
                else:
                    #if the input lang is not eng, translate the text and return it.
                    SetAssistantStatus("Translating... ")
                    return QueryModifier(UniversalTranslator(Text))
        
        except Exception as e:
            pass
        
#main execution block.
if __name__ == "__main__":
    while True:
        #continuously perform speech recognition and print the recognized text.
        Text = SpeechRecognition()
        print(Text)

