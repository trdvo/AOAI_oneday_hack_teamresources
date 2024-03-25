from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv
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
import os
import pandas as pd
import pyodbc
from langchain_openai import AzureChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from common.prompts import MSSQL_AGENT_PREFIX, MSSQL_AGENT_SUFFIX, MSSQL_AGENT_FORMAT_INSTRUCTIONS
from langchain.agents import AgentExecutor
from langchain.callbacks.manager import CallbackManager
from IPython.display import Markdown, HTML, display


def printmd(string):
    display(Markdown(string))

load_dotenv()


def query_database(query):
    # Configuration for the database connection
    db_config = {
        'drivername': 'mssql+pyodbc',
        'username': os.environ["SQL_SERVER_USERNAME"] + '@' + os.environ["SQL_SERVER_NAME"],
        'password': os.environ["SQL_SERVER_PASSWORD"],
        'host': os.environ["SQL_SERVER_NAME"],
        'port': 1433,
        'database': os.environ["SQL_SERVER_DATABASE"],
        'query': {'driver': 'ODBC Driver 17 for SQL Server'},
    }

    # Create a URL object for connecting to the database
    db_url = URL.create(**db_config)

    # Connect to the Azure SQL Database using the URL string
    engine = create_engine(db_url)

    # Test the connection using the SQLAlchemy 2.0 execution style
    with engine.connect() as conn:
        try:
            # Use the text() construct for safer SQL execution
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.fetchone()
            print("Connection successful!")
            print(version)
        except Exception as e:
            print(e)

    llm = AzureChatOpenAI(
        deployment_name=os.environ["GPT35_DEPLOYMENT_NAME"],
        temperature=0.5,
        max_tokens=2000,
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2023-08-01-preview")

    # Let's create the db object
    db = SQLDatabase.from_uri(db_url)

    # Natural Language question (query)
    QUESTION = query

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent_executor = create_sql_agent(
        prefix=MSSQL_AGENT_PREFIX,
        suffix=MSSQL_AGENT_SUFFIX,
        format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS,
        llm=llm,
        toolkit=toolkit,
        top_k=30,
        agent_type="openai-tools",
        verbose=True
    )

    # As we know by now, Agents use expert/tools. Let's see which are the tools for this SQL Agent
    agent_executor.tools
    try:
        response = agent_executor.invoke(QUESTION)
    except Exception as e:
        response = str(e)

    print(response)
    print(response.keys())
    printmd(response["output"])
    return response["output"]

