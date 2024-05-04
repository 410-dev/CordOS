import requests
import google.generativeai as genai

import kernel.registry as Registry
import kernel.journaling as Journaling


def fetchApiKey():
    if Registry.read("SOFTWARE.CordOS.Experimental.LLMAssistant.APIKeyFromFetch", default="0") == "1":
        Journaling.record("INFO", "Fetching API key from URL is enabled.")
        if Registry.read("SOFTWARE.CordOS.Experimental.LLMAssistant.FetchURL", default="") == "":
            Journaling.record("ERROR", "Fetch URL is not set.")
            return ""
        else:
            url = Registry.read("SOFTWARE.CordOS.Experimental.LLMAssistant.FetchURL")
            Journaling.record("INFO", f"Fetching API key from URL: {url} (Registry at SOFTWARE.CordOS.Experimental.LLMAssistant.FetchURL)")
            response = requests.post(url)
            return response.text.strip()
    else:
        Journaling.record("INFO", "Fetching API key from URL is disabled.")
        return Registry.read("SOFTWARE.CordOS.Experimental.LLMAssistant.APIKey", default="")


def sendRequest(userContent):
    genai.configure(api_key=fetchApiKey())
    model = genai.GenerativeModel(Registry.read("SOFTWARE.CordOS.Experimental.LLMAssistant.Model", default="gemini-pro"))
    response = model.generate_content(userContent)
    return response.text

