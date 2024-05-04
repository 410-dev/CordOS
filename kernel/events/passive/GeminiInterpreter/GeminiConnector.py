import requests

import google.generativeai as genai

def fetchApiKey(authToken):
    url = "https://hysong.dev/keystore/api/labs/labid-8356941/api-1.0-key-240504"
    response = requests.post(url, data={"auth": authToken})
    return response.text.strip()


def sendRequest(userContent):
    genai.configure(api_key=fetchApiKey(""))
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(userContent)
    return response.text

