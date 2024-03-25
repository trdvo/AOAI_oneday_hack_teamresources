from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
import openai
from openai import AzureOpenAI
import os
import requests
from dotenv import load_dotenv

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve static files
@app.get("/")
async def main():
    return FileResponse("public/index.html")

# chatbot API to be extended with OpenAI code
@app.post("/chat")
async def chat(request: Request):
    json = await request.json()
    print(json)

    ############################
    load_dotenv()
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID")
    print(f"endpoint: {endpoint}, api_key: {api_key}, deployment: {deployment}")
    client = openai.AzureOpenAI(
        base_url=f"{endpoint}/openai/deployments/{deployment}/extensions",
        api_key=api_key,
        api_version="2023-08-01-preview",
    )

    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "user", "content": json["message"]},
            #{"role": "assistant", "content": ""}  # The assistant message is optional
        ],
        extra_body={
            "dataSources": [
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": os.environ["AZURE_AI_SEARCH_ENDPOINT"],
                        "key": os.environ["AZURE_AI_SEARCH_API_KEY"],
                        "indexName": os.environ["AZURE_AI_SEARCH_INDEX"]
                    }
                }
            ]
        }
    )
    # extract the message content from the completion which looks like this:
    print(str(completion.choices[0].message.content))
    return {"message": str(completion.choices[0].message.content)}
# Image generattion API to be extended with OpenAI code
@app.post("/generateImage")
async def generateImage(request: Request):
    json = await request.json()
    print(json)

    ############################
    ### Add OpenAI code here ###
    ############################

    return {"url": "https://via.placeholder.com/100"}

app.mount("/", StaticFiles(directory="public"), name="ui")
