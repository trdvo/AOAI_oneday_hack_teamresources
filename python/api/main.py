from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
import openai
from openai import AzureOpenAI
import os
import requests
from dotenv import load_dotenv
from PIL import Image
import json
from database_app import query_database
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
    print(request)
    json = await request.json()
    print(json)
    message_from_db = query_database(json["message"])

    # extract the message content from the completion which looks like this:
    return {"message": str(message_from_db)}






# chatbot API to be extended with OpenAI code
@app.post("/chat")
async def chat2(request: Request):
    print(request)
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
                        "indexName": os.environ["AZURE_AI_SEARCH_INDEX"],
                        "topNDocuments": 10,
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
    json_image = await request.json()
    print(json_image)
    load_dotenv()
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID")
    # convert dict into a sentence.  It should look like "The {key} is {value}"
    instructions = """
    Create a text prompt for DALLE that will generate an image of a 3D Pixar-like style character
    that will be my avatar.
    Here is an example of the text prompt where the face was simmetric, oval, the eyebrows were medium thin,
    the eyes were brown, the beard and moustache were 4mm full, and the hair was short and brown.
    Create me a portrait of 3d Pixar-like style character that will be my avatar. I am caucausian male, 
    have simmetric, oval face with medium thin eyebrows, brown eyes, 4mm full beard and moustache, short brown hair.
    Now create something similar with the following characteristics:
    If the description is "None", omit that part of the description. Remember that the Avatar is wearing official
    Manchester United jersey and red baseball cap.
    """
    for key in json_image:
        if json_image[key] == "":
            json_image[key] = "None"
        prompt = f"The {key} is {json_image[key]}."
        instructions += prompt + " "
        
    client_image_prompt = openai.AzureOpenAI(
        base_url=f"{endpoint}/openai/deployments/{deployment}",
        api_key=api_key,
        api_version="2023-08-01-preview",
    )
    completion = client_image_prompt.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "user", "content": instructions},
            # {"role": "assistant", "content": ""}  # The assistant message is optional
        ],
    )
    adjusted_prompt = completion.choices[0].message.content
    print("adjusted_prompt: ", adjusted_prompt)
    #
    client = openai.AzureOpenAI(
        azure_endpoint="https://aoioiavolvoteam2.openai.azure.com/",
        api_key=api_key,
        api_version="2024-02-01",
    )

    result = client.images.generate(
        model="Dalle3", # the name of your DALL-E 3 deployment
        prompt=adjusted_prompt,
        n=1
    )
    print(result.data[0].url)
    return {"url": result.data[0].url}

app.mount("/", StaticFiles(directory="public"), name="ui")
